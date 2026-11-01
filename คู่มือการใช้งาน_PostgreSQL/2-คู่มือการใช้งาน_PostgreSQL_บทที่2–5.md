# บทที่ 2–5

> หนังสือ: คู่มือการใช้งาน PostgreSQL สำหรับ DevOps Engineer, Cloud Engineer และ DBA  
> ส่วนที่ 1 ปฐมบทและสถาปัตยกรรม  
> โทน: ทางการ กระชับ เน้นใช้งานจริง

---

# บทที่ 2 บทบาท DevOps, Cloud Engineer และ DBA

## 1. เรื่อง
บทบาท หน้าที่ ความรับผิดชอบ และจุดเชื่อมโยงการทำงานร่วมกันระหว่าง DevOps Engineer, Cloud Engineer และ DBA ในระบบ PostgreSQL Production

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้ผู้อ่านเข้าใจขอบเขตหน้าที่ของแต่ละบทบาทอย่างชัดเจน  
2. เพื่อลดความซ้ำซ้อนและช่องว่างความรับผิดชอบ (Responsibility Gap)  
3. เพื่อกำหนดจุดส่งต่อ (Handover Point) ระหว่างทีมในวงจรชีวิตฐานข้อมูล  
4. เพื่อให้การ Monitoring และการแจ้งเตือนมีเจ้าของที่ชัดเจน

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบบท ผู้อ่านสามารถ:
- อธิบายหน้าที่หลักของ DevOps Engineer, Cloud Engineer และ DBA ได้
- ระบุว่าเหตุการณ์ใดควรเป็นของทีมใด และส่งต่อเมื่อใด
- ออกแบบ RACI Matrix สำหรับงาน PostgreSQL Production ได้
- กำหนดเจ้าของ Metric, Alert และ Runbook ได้

## 4. เนื้อหาโดยย่อ กระชับ
- **DevOps Engineer** ดูแล Pipeline, Automation, Infrastructure as Code, Observability Pipeline และการ Deploy  
- **Cloud Engineer** ดูแลโครงสร้าง Cloud, Network, Storage, Identity, Cost และ Managed Service  
- **DBA** ดูแลฐานข้อมูลเชิงลึก: Performance, Backup/Recovery, Replication, Security, Migration, Data Integrity  
- ทั้งสามบทบาท **ต้องทำงานบนข้อมูลชุดเดียวกัน** คือ Metric, Log, Alert และ Runbook  
- ความล้มเหลวส่วนใหญ่เกิดจาก **“ไม่มีใครเป็นเจ้าของ”** ไม่ใช่ “ไม่มีคนเก่ง”  
- หลักการสำคัญ: **Single Owner per Task, Shared Visibility**

## 5. ประโยชน์ที่ได้รับ
- ลดเวลาตอบสนองเหตุการณ์ เพราะรู้ว่าต้องแจ้งใคร
- ลดการทำงานซ้ำซ้อนและลดความขัดแย้งภายในทีม
- ทำให้ Alert ทุกตัวมีเจ้าของและ Runbook
- ทำให้การเปลี่ยนผ่านระบบ (Deploy, Migration, Upgrade) มีผู้อนุมัติชัดเจน
- ทำให้การวัดผลด้วย KPI มีความหมาย เพราะมีผู้รับผิดชอบตัวชี้วัด

## 6. ข้อควรระวัง
- **ห้ามใช้คำว่า “ทีมฐานข้อมูลดูแลทั้งหมด”** เพราะทำให้ DevOps และ Cloud Engineer ไม่มีส่วนร่วมใน Observability  
- **ห้ามให้ DBA ถือสิทธิ์ Superuser ในงานประจำวัน** ของแอปพลิเคชัน  
- **ห้ามให้ DevOps ถือสิทธิ์แก้ Parameter ฐานข้อมูลโดยไม่ผ่าน Change Process**  
- **ห้ามให้ Cloud Engineer ปรับ Security Group หรือ Network โดยไม่แจ้ง DBA** เพราะอาจตัดการเชื่อมต่อ Replication  
- **ห้ามปล่อยให้ Alert ไม่มีเจ้าของ** แม้เพียงข้อเดียว

## 7. ข้อดีของการแบ่งบทบาทชัดเจน
- การตัดสินใจเร็วขึ้น เพราะไม่ต้องถามว่าใครรับผิดชอบ
- Audit และ Compliance ทำได้ง่าย
-  onboarding ทีมใหม่ทำได้เร็ว เพราะมี RACI ชัด
- Incident Response มีลำดับขั้นตอนที่ทำซ้ำได้
- วัด KPI รายบุคคลและรายทีมได้อย่างเป็นธรรม

## 8. ข้อเสีย / ข้อจำกัด
- หากแบ่งเข้มเกินไปจะเกิด Silo และช่องว่างที่ไม่มีใครดูแล
- ต้องลงทุนเวลาในการทำ RACI และทบทวนเป็นระยะ
- องค์กรขนาดเล็กอาจต้องรวมบทบาท (เช่น DevOps + Cloud Engineer)
- การเปลี่ยนบทบาท (Role Shift) อาจทำให้เกิดช่วงสุญญากาศชั่วคราว

## 9. ข้อห้าม
- ห้ามให้บทบาทหนึ่งถือสิทธิ์ Superuser ของอีกระบบโดยไม่มีการบันทึก
- ห้ามส่งต่อ Incident โดยไม่มี Handover Note
- ห้ามแก้ Runbook โดยไม่แจ้งเจ้าของ Runbook
- ห้ามใช้ Alert ช่องทางเดียวสำหรับทุก Severity
- ห้ามใช้ Production เป็นที่ทดลองคำสั่งใหม่ของบทบาทใดบทบาทหนึ่ง

## 10. รายละเอียด

### 10.1 หน้าที่หลักของแต่ละบทบาท

| ด้านงาน | DevOps Engineer | Cloud Engineer | DBA |
|---|---|---|---|
| Provisioning | Infrastructure as Code, Pipeline | Cloud Resource, Network, IAM | Cluster, Role, Database |
| Configuration | Config Management | Cloud Config, Secret Manager | PostgreSQL Parameter, pg_hba |
| Deployment | CI/CD, Blue-Green, Canary | Load Balancer, DNS | Migration Script, Extension |
| Observability | Prometheus, Grafana, Log Pipeline | Cloud Monitoring Integration | Metric เฉพาะฐานข้อมูล, Runbook |
| Alerting | Alert Rule, Routing | Cloud Alert, Pager | Runbook, Severity Definition |
| Backup | Automation Pipeline | Storage Bucket, Lifecycle | pgBackRest, PITR, Restore Test |
| HA | Automation, Health Check | Network, Load Balancer | Patroni, Replication, Failover |
| Security | Secret Management, SAST | IAM, KMS, WAF | Role, RLS, pgcrypto, pgAudit |
| Performance | Profiling แอป | Resource Sizing | Tuning, Index, Query Plan |
| Incident | First Responder (ระบบ) | First Responder (Cloud) | First Responder (ฐานข้อมูล) |
| Capacity | Auto Scaling | Cost & Quota | Partitioning, Archiving |

### 10.2 RACI Matrix ตัวอย่าง

R = Responsible (ผู้ลงมือ), A = Accountable (ผู้อนุมัติ/รับผิดชอบผล), C = Consulted (ผู้ให้คำปรึกษา), I = Informed (ผู้รับทราบ)

| งาน | DevOps | Cloud Engineer | DBA |
|---|---|---|---|
| ติดตั้ง PostgreSQL Cluster | C | C | **A/R** |
| ตั้งค่า Prometheus Scrape | **A/R** | C | C |
| ตั้งค่า Alertmanager Routing | **A/R** | C | C |
| เขียน Runbook ของ Alert ฐานข้อมูล | C | I | **A/R** |
| Provision Storage สำหรับ Backup | C | **A/R** | C |
| ตั้งค่า Network สำหรับ Replication | I | **A/R** | C |
| เปิด TLS บน PostgreSQL | C | I | **A/R** |
| Migration Script บน Production | **A** | I | **R** |
| Failover ซ้อม | C | I | **A/R** |
| Restore Test | C | C | **A/R** |
| Upgrade Major Version | **A** | C | **R** |
| Incident Postmortem | **R** | **R** | **R** |

### 10.3 จุดส่งต่อ (Handover Point)

```text
[Cloud Engineer] Provision VM + Network + Storage
        │
        ▼
[DevOps Engineer] ติดตั้ง Agent, Exporter, Prometheus, CI/CD
        │
        ▼
[DBA] ตั้งค่า PostgreSQL, Role, Backup, Replication
        │
        ▼
[DevOps + DBA] ร่วมตั้ง Alert Rule + Runbook
        │
        ▼
[ทั้งสามทีม] On-call Rotation และ Incident Response
```

### 10.4 หลักการ On-call ร่วม
1. **One Incident Owner ต่อหนึ่งเหตุการณ์** ณ เวลาหนึ่ง  
2. **ทุก Alert มี Primary Owner และ Secondary**  
3. **ทุก Runbook มีวันทบทวน (Review Date)**  
4. **ทุก Incident มี Incident Record เดียว** แม้หลายทีมเกี่ยวข้อง  
5. **ทุก PSR มี Action Item ที่มีเจ้าของและวันที่**

### 10.5 ตัวอย่าง Alert Ownership

| Alert | Primary Owner | Secondary | Runbook |
|---|---|---|---|
| PostgresDown | DBA | DevOps | `C08-postgres-down.md` |
| PostgresConnectionsHigh | DBA | DevOps | `C03-connection-limit-locking.md` |
| DiskSpaceLow (pg data) | Cloud Engineer | DBA | `C04-disk-full.md` |
| BackupTooOld | DBA | Cloud Engineer | `C07-backup-recovery.md` |
| SslCertificateExpiringSoon | DBA | Cloud Engineer | `C10-security.md` |
| PatroniPrimaryCountNotOne | DBA | DevOps | `C08-replication-lag-slot-failover.md` |
| NodeExporterDown | DevOps | Cloud Engineer | `C11-monitoring.md` |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: เหตุการณ์ Connection เต็ม

```text
14:30:15  Alert PostgresConnectionsHigh (firing, severity=warning) → Alertmanager → dba-email
14:31:05  DBA เปิด Runbook C03 ตรวจ:
            SELECT state, count(*) FROM pg_stat_activity GROUP BY state;
          พบ idle in transaction จำนวนมาก
14:33:20  DBA แจ้ง DevOps: "ตรวจ PgBouncer pool_mode และ client disconnect logic"
14:40:00  DevOps ลดจำนวน client ที่ค้าง และเพิ่ม idle_in_transaction_session_timeout
14:55:00  Alert Resolved
15:30:00  PSR: Action = เพิ่ม Alert "IdleInTransaction>5m" + เพิ่ม Runbook link
```

### ตัวอย่างที่ 2: เหตุการณ์ Network ตัด ทำให้ Replication Lag

```text
10:30:15  Cloud Engineer เปลี่ยน Security Group โดยไม่แจ้ง
10:30:40  Replication Lag เพิ่มเป็น 512 MB
10:30:50  Alert PostgresReplicationLagHigh (critical) → DBA + DevOps + Cloud Engineer
10:31:00  DBA พบ stream ขาด; DevOps พบ exporter scrape fail; Cloud Engineer เห็น SG เปลี่ยนล่าสุด
10:32:00  คืนค่า SG และ Restart Replica
10:35:00  Alert Resolved
PSR: Action = ต้องมี Change Approval จาก DBA ก่อนแก้ Security Group ของ DB Subnet
```

## 12. สรุปย่อ จำง่าย
- **DevOps** = Automation, Pipeline, Observability, Deploy  
- **Cloud Engineer** = Network, Storage, IAM, Cost, Managed Service  
- **DBA** = ฐานข้อมูลเชิงลึก Performance, Backup, Replication, Security, Migration  
- **RACI** คือเครื่องมือหลักในการกำหนดเจ้าของ  
- **ทุก Alert ต้องมี Runbook และเจ้าของ**  
- **ทุก Incident มี Incident Record เดียว**  
- **ทุก PSR มี Action Item ที่วัดได้**

ประโยคจำ: **“ทุก Metric มีคนดู ทุก Alert มีคนตอบ ทุก Incident มีคนสรุป”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Google SRE Book: https://sre.google/sre-book/
- Prometheus Documentation: https://prometheus.io/docs/
- ITIL 4 Service Management Practices
- GridCare Workshop: `monitoring/runbooks/` และ Incident Record Template
- Outline หลักสูตร Advanced PostgreSQL for Enterprise Production (PEA)

---

# บทที่ 3 สถาปัตยกรรม PostgreSQL โดยย่อ

## 1. เรื่อง
โครงสร้างภายในของ PostgreSQL ที่จำเป็นต่อการตัดสินใจในงาน DevOps, Cloud และ DBA

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจว่าองค์ประกอบใดทำให้ PostgreSQL ทำงานใน Production ได้  
2. เพื่อให้เลือก Metric และ Parameter ที่ตรงกับสถาปัตยกรรมจริง  
3. เพื่อให้แปลความหมายของ Log, Metric และ Plan ได้ถูกต้อง  
4. เพื่อให้สามารถวินิจฉัยปัญหาได้อย่างเป็นระบบ

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย Process ของ PostgreSQL หลัก ๆ ได้
- อธิบายหน้าที่ของ WAL, Shared Buffers, Background Writer, Checkpointer
- อธิบาย MVCC โดยย่อ
- อธิบายความแตกต่างของ Physical และ Logical Storage
- เลือก Metric สำคัญตามองค์ประกอบนั้น ๆ

## 4. เนื้อหาโดยย่อ
PostgreSQL แบ่งเป็น **Postmaster** และ **Backend Processes**  
Backend Process สำคัญ ได้แก่:
- `postgres` (Postmaster/Parent)
- `checkpointer` (เขียน Dirty Page ลงดิสก์เป็นรอบ)
- `background writer` (เขียน Page สำรองล่วงหน้า)
- `walwriter` (เขียน WAL)
- `autovacuum launcher` (เรียก Worker ทำ Vacuum/Analyze)
- `logical replication launcher`
- `client backend` (Process ของผู้ใช้)

Storage สำคัญ ได้แก่:
- `base/` (Data File)
- `pg_wal/` (WAL)
- `pg_stat/`, `pg_stat_statements`, `pg_subtrans`
- Tablespace, Table, Index, TOAST, Free Space Map

หลักการเขียน-อ่าน:
- **เขียน** → เขียน WAL ก่อน แล้วค่อยเขียน Data Page ทีหลัง
- **อ่าน** → อ่านจาก Shared Buffers ก่อน ถ้าไม่พบจึงอ่านจากดิสก์
- **MVCC** → เก็บหลายเวอร์ชันของแถวไว้เพื่อให้ Transaction เห็นข้อมูลที่สอดคล้องกัน

## 5. ประโยชน์ที่ได้รับ
- เลือก Metric ได้ตรงกับองค์ประกอบ เช่น Checkpointer → `pg_stat_checkpointer`
- เข้าใจว่า `shared_buffers` ไม่ใช่ Cache ทั้งหมดของระบบ (`effective_cache_size` คือ Hint)
- เข้าใจว่า `WAL` สำคัญต่อ Backup, Replication และ PITR
- อ่าน Log เช่น `still waiting for AccessExclusiveLock` ได้เร็วขึ้น
- ออกแบบ Index, Partition, Bloat ได้มีหลักการ

## 6. ข้อควรระวัง
- `shared_buffers` ที่สูงเกินไปอาจทำให้ระบบขาด Memory ให้ Process อื่น  
- `work_mem` เป็นการตั้งต่อ Operation ไม่ใช่ต่อ Session ทั้งหมด  
- การเพิ่ม `max_connections` ทำให้ Process เพิ่ม และ Memory ต่อ Process เพิ่ม  
- `wal_level`, `max_wal_senders`, `max_replication_slots` ต้องตั้งก่อนใช้ Replication  
- `checkpoint_timeout` สั้นเกินไปทำให้มี I/O หนัก

## 7. ข้อดี
- สถาปัตยกรรมเปิดให้ปรับแต่งได้ละเอียด
- MVCC ทำให้การอ่านไม่บล็อกการเขียน
- WAL ทำให้ทำ PITR และ Replication ได้
- Extension ช่วยเพิ่มความสามารถโดยไม่ต้องรอ Core

## 8. ข้อเสีย
- Parameter มีจำนวนมาก ต้องเข้าใจบริบทก่อนปรับ
- MVCC ทำให้เกิด Bloat ถ้า Vacuum ไม่ทัน
- WAL ที่ไม่ได้จัดการอาจทำให้ Disk เต็ม
- Connection ที่มากเกินไปทำให้ Memory และ CPU หนัก

## 9. ข้อห้าม
- ห้ามลบหรือแก้ไฟล์ใน `pg_wal/`, `pg_xact/` โดยตรง
- ห้ามตั้ง `fsync = off` บน Production
- ห้ามใช้ `shared_buffers` เกิน 40% ของ RAM ทั้งเครื่องโดยไม่ตรวจสอบ
- ห้ามเปิด `archive_mode` ก่อนสร้าง Stanza ใน pgBackRest
- ห้ามลบ `pg_wal` เพื่อแก้ Disk เต็ม

## 10. รายละเอียด

### 10.1 Process ที่ต้องรู้

| Process | หน้าที่ | Metric ที่เกี่ยวข้อง |
|---|---|---|
| `postgres` | Postmaster รับ connection เปิด Backend | `pg_up`, `pg_postmaster_start_time` |
| `checkpointer` | เขียน Dirty Page ลงดิสก์เป็นรอบ | `pg_stat_checkpointer_num_timed`, `pg_stat_checkpointer_num_requested` |
| `background writer` | เขียน Page ล่วงหน้า ลดการชะงัก | `pg_stat_bgwriter_buffers_clean` |
| `walwriter` | เขียน WAL Buffer ลงดิสก์ | `pg_stat_wal_wal_buffers_full`, `pg_stat_wal_wal_write` |
| `autovacuum launcher` | เรียก Autovacuum Worker ตามเกณฑ์ | `pg_stat_user_tables_n_dead_tup`, `pg_stat_progress_vacuum` |
| `logical replication launcher` | ดูแล Logical Replication | `pg_stat_replication_slots` |
| `client backend` | Process ของผู้ใช้แต่ละ session | `pg_stat_activity_count`, `pg_stat_activity_max_tx_duration` |

### 10.2 Storage Layer

```text
PGDATA=/var/lib/postgresql/17/main
├── base/               ← Data File ของแต่ละ Database
├── global/             ← Catalog ของทั้ง Cluster
├── pg_wal/             ← Write-Ahead Log (แต่ละไฟล์ 16 MB)
├── pg_wal/archive_status/
├── pg_xact/            ← Commit Log
├── pg_stat/            ← Cumulative Statistics
├── pg_stat_tmp/
├── pg_subtrans/
├── pg_multixact/
├── pg_tblspc/          ← Tablespace
└── postgresql.auto.conf
```

### 10.3 MVCC โดยย่อ
- แต่ละแถวมี `xmin` (Transaction ที่สร้าง) และ `xmax` (Transaction ที่ลบ/อัปเดต)
- `UPDATE` ใน PostgreSQL = สร้างแถวใหม่และตั้ง `xmax` ให้แถวเดิม
- `VACUUM` จะลบแถวที่ Commit แล้วและไม่มีใครเห็นอีก
- `REPEATABLE READ` และ `SERIALIZABLE` ใช้ Snapshot ในการมองเห็นข้อมูล

### 10.4 Write Path โดยย่อ

```text
Client → Postmaster → Backend
   │
   ▼
Shared Buffers → Dirty Page
   │
   ▼
WAL Buffer → walwriter → pg_wal/ (fsync)
   │
   ▼
checkpointer → Data File
```

### 10.5 Read Path โดยย่อ

```text
Client → Backend → Shared Buffers
                       │
                       ├── Hit → return
                       └── Miss → Read Data File → Put in Shared Buffers → return
```

### 10.6 Metric สำคัญตามองค์ประกอบ

| องค์ประกอบ | Metric หลัก |
|---|---|
| Availability | `pg_up`, `pg_postmaster_start_time_seconds` |
| Connection | `pg_stat_activity_count`, `pg_settings_max_connections` |
| Transaction | `pg_stat_database_xact_commit`, `pg_stat_database_xact_rollback` |
| Buffer | `pg_stat_database_blks_hit`, `pg_stat_database_blks_read` |
| WAL | `pg_stat_wal_wal_write`, `pg_stat_wal_wal_sync`, `pg_ls_waldir` |
| Checkpointer | `pg_stat_checkpointer_num_timed`, `buffers_written` |
| Autovacuum | `pg_stat_user_tables_n_dead_tup`, `last_autovacuum` |
| XID | `pg_database_wraparound_age_datfrozenxid_seconds` |
| Replication | `pg_stat_replication_pg_wal_lsn_diff`, `pg_replication_slots_pg_wal_status` |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ดู Process ของ PostgreSQL

```bash
ps -u postgres -o pid,ppid,rss,cmd --forest | grep -v grep | grep postgres
```

ผลลัพธ์:
```text
   1234     1   156 /usr/lib/postgresql/17/bin/postgres -D /var/lib/postgresql/17/main
   1236  1234  1024  \_ postgres: checkpointer
   1237  1234   932  \_ postgres: background writer
   1238  1234   876  \_ postgres: walwriter
   1239  1234   924  \_ postgres: autovacuum launcher
   1240  1234   748  \_ postgres: logical replication launcher
```

### ตัวอย่างที่ 2: ดู Backend Type ด้วย SQL

```sql
SELECT pid, backend_type, backend_start
FROM pg_stat_activity
ORDER BY backend_type;
```

ผลลัพธ์:
```text
  pid  |         backend_type         |         backend_start         
-------+------------------------------+-------------------------------
 21242 | autovacuum launcher          | 2026-10-31 03:46:07.98938+00
 21239 | background writer            | 2026-10-31 03:46:07.968842+00
 21238 | checkpointer                 | 2026-10-31 03:46:07.970745+00
 21328 | client backend               | 2026-10-31 03:52:42.270116+00
 21243 | logical replication launcher | 2026-10-31 03:46:07.991464+00
 21241 | walwriter                    | 2026-10-31 03:46:07.989576+00
(6 rows)
```

### ตัวอย่างที่ 3: ตรวจสอบ WAL ปัจจุบัน

```sql
SELECT pg_current_wal_lsn(), pg_walfile_name(pg_current_wal_lsn());
```

ผลลัพธ์:
```text
 pg_current_wal_lsn |       pg_walfile_name       
--------------------+-----------------------------
 0/170000D8         | 000000010000000000000017
(1 row)
```

### ตัวอย่างที่ 4: ตรวจสอบ Checkpointer

```sql
CHECKPOINT;
SELECT num_timed, num_requested, buffers_written FROM pg_stat_checkpointer;
```

ผลลัพธ์:
```text
 num_timed | num_requested | buffers_written 
-----------+---------------+-----------------
         2 |             1 |             240
```

> ✅ `num_requested` เพิ่มจาก 0 เป็น 1 แสดงว่า Checkpoint ที่สั่งด้วยคำสั่งเพิ่มขึ้นจริง

### ตัวอย่างที่ 5: ดูขนาด WAL Directory

```sql
SELECT pg_size_pretty(sum(size)) AS pg_wal_size FROM pg_ls_waldir();
```

ผลลัพธ์:
```text
 pg_wal_size 
-------------
 768 MB
```

## 12. สรุปย่อ จำง่าย
- **Postmaster** รับ Connection และ **Backend Process** ทำงาน  
- **Checkpointer / Background Writer / walwriter / Autovacuum Launcher** คือแกนของสถาปัตยกรรม  
- **WAL เขียนก่อน Data Page** = หลักสำคัญของ Crash Safety  
- **MVCC** ทำให้อ่านไม่บล็อกเขียน แต่ทำให้เกิด Bloat  
- **Metric ต้องผูกกับ Process และ Storage ไม่ใช่สุ่มดู**

ประโยคจำ: **“WAL ก่อน Page, Buffer ก่อน Disk, Metric ก่อนแก้”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Architecture: https://www.postgresql.org/docs/17/architecture.html
- PostgreSQL Documentation — WAL: https://www.postgresql.org/docs/17/wal.html
- PostgreSQL Documentation — MVCC: https://www.postgresql.org/docs/17/mvcc.html
- PostgreSQL Documentation — Monitoring: https://www.postgresql.org/docs/17/monitoring.html
- GridCare Workshop Day 1–2: Lab 3.2, Lab 3.4, Lab 4.1, Lab 4.2

---

# บทที่ 4 วงจรชีวิตฐานข้อมูล Production

## 1. เรื่อง
วงจรชีวิตของฐานข้อมูล PostgreSQL ใน Production ตั้งแต่การวางแผนจนถึงการเลิกใช้งาน

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เห็นภาพรวมว่าฐานข้อมูล Production มีขั้นตอนอะไรบ้างตลอดอายุการใช้งาน  
2. เพื่อให้วางแผนงานล่วงหน้าและลดการเปลี่ยนแปลงแบบเร่งด่วน  
3. เพื่อให้แต่ละบทบาทรู้ว่าตนอยู่ส่วนใดของวงจร  
4. เพื่อให้กำหนด KPI และ Monitoring ที่เหมาะสมกับแต่ละระยะ

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย 8 ระยะของวงจรชีวิตฐานข้อมูล Production
- ระบุสิ่งที่ต้องทำในแต่ละระยะ
- ระบุ Metric และ Alert ที่สำคัญในแต่ละระยะ
- วางแผน Maintenance Calendar รายปีได้

## 4. เนื้อหาโดยย่อ
วงจรชีวิตฐานข้อมูล Production ประกอบด้วย 8 ระยะ:
1. **Plan** — วางแผน Capacity, SLO, Backup, HA, Security
2. **Provision** — เตรียมเครื่องและติดตั้ง PostgreSQL
3. **Configure** — ตั้งค่า Parameter, Role, TLS, pg_hba, Logging
4. **Operate** — ใช้งานประจำวัน Monitoring, Maintenance, Backup
5. **Optimize** — ปรับ Performance, Index, Partition, VACUUM
6. **Protect** — Security, RLS, Masking, Audit, Backup Test
7. **Evolve** — Migration, Upgrade, ขยาย Scale
8. **Retire** — Archive, Decommission, Data Retention

หลักการ: **ทุกระยะต้องมี Metric, Alert และ Runbook รองรับ**

## 5. ประโยชน์ที่ได้รับ
- ลดการเปลี่ยนแบบเร่งด่วนที่ทำให้เกิด Incident
- รู้ว่าต้องมี Metric อะไรในแต่ละระยะ
- ทำให้ Timeline ของ Upgrade และ Migration ชัดเจน
- ลดความเสี่ยงตอน Decommission และ Data Retention
- ทำให้ Cost Planning แม่นยำขึ้น

## 6. ข้อควรระวัง
- **ห้ามข้ามระยะ Protect** เพราะความปลอดภัยไม่ใช่ Optional  
- **ห้าม Upgrade โดยไม่ทดสอบ Restore Test** ของ Backup ล่าสุด  
- **ห้าม Decommission โดยไม่ Archive ข้อมูลตามข้อกำหนด**  
- **ห้าม Optimize โดยไม่มี Baseline Metric**  
- **ห้าม Provision โดยไม่วาง SLO และ RTO/RPO**

## 7. ข้อดี
- มี Timeline ชัด ทำให้ทีมวางแผน On-call และ Maintenance ได้
- มี KPI ต่อระยะ ทำให้วัดผลได้
- มีจุดตรวจ (Gate) ทุกขั้น ลดความเสี่ยง
- ทำให้ Cost และ Capacity Planning เป็นระบบ

## 8. ข้อเสีย
- ต้องลงทุนทำ Baseline และ Documentation
- บางองค์กรไม่มีเจ้าของชัดเจนทำให้วงจรขาดตอน
- ต้องทบทวนทุกปี มิฉะนั้นแผนจะเก่า

## 9. ข้อห้าม
- ห้าม Provision เครื่องใหม่โดยไม่ระบุ SLO และ Backup Strategy
- ห้าม Configure Production โดยไม่บันทึกใน Change Log
- ห้าม Optimize โดยไม่เก็บ Baseline และวัด After
- ห้าม Retire โดยไม่ Archive และไม่ลบ Credential
- ห้าม Upgrade โดยไม่มี Rollback Plan

## 10. รายละเอียด

### 10.1 ตาราง 8 ระยะ พร้อมกิจกรรมและ Metric

| ระยะ | กิจกรรมหลัก | Metric สำคัญ | Alert สำคัญ |
|---|---|---|---|
| Plan | SLO, RTO/RPO, Capacity, Cost | SLI, Target SLO | ไม่มี (ตรวจ SLO Report) |
| Provision | VM, Storage, Network, Install | `pg_up`, `node_boot_time` | `PostgresDown` |
| Configure | Parameter, Role, TLS, Logging | `pg_settings_*`, `pg_file_settings_errors` | `PostgresConfigReloadFailed` |
| Operate | Monitoring, Backup, Vacuum | `pg_stat_database_*`, `backup_age` | `BackupTooOld`, `PostgresConnectionsHigh` |
| Optimize | Index, VACUUM, Partition | `pg_stat_statements`, `n_dead_tup` | `PostgresBloatHigh` |
| Protect | RLS, Masking, Audit | `pgaudit_log`, `pg_stat_ssl` | `SslCertificateExpiringSoon` |
| Evolve | Migration, Upgrade | `pg_upgrade`, `pg_stat_progress_vacuum` | `PatroniPrimaryCountNotOne` |
| Retire | Archive, Decommission | `pg_database_size_bytes` | ไม่มี (ใช้ Process Gate) |

### 10.2 Maintenance Calendar ตัวอย่าง

| รอบ | งาน | ผู้รับผิดชอบ | หลักฐาน |
|---|---|---|---|
| รายวัน | ตรวจ Alert, Backup Success, XID Age | DBA | Health Check Log |
| รายสัปดาห์ | Weekly Report: Index ซ้ำ, FK ไม่มี Index, Sequence > 85% | DBA | weekly_report.sql |
| รายเดือน | Restore Test, Patch OS | DBA + Cloud Engineer | restore_test.sh log |
| รายไตรมาส | Capacity Review, Parameter Review | ทั้งสามทีม | Review Notes |
| รายปี | Major Version Review, DR Drill | ทั้งสามทีม | Drill Report |

### 10.3 Gate การผ่านระยะ

ทุกระยะควรมี **Gate** ที่ต้องผ่านก่อนไประยะถัดไป:

```text
Plan ──Gate1(SLO approved)──► Provision ──Gate2(Postgres up + Backup ok)──►
Configure ──Gate3(Parameter + TLS + Role verified)──► Operate ──Gate4(Alert + Runbook ready)──►
Optimize ──Gate5(Baseline & After measured)──► Protect ──Gate6(Audit + RLS tested)──►
Evolve ──Gate7(Migration tested + Rollback ok)──► Retire ──Gate8(Data archived + Access revoked)
```

### 10.4 ตัวอย่าง KPI ต่อระยะ

| ระยะ | KPI |
|---|---|
| Provision | เวลาติดตั้งสำเร็จ 100% ภายใน SLA ที่กำหนด |
| Configure | Parameter ผ่าน `pg_file_settings` 100% |
| Operate | Availability ≥ 99.9%, Backup Success 100% |
| Optimize | Query P95 ลดลง ≥ 30% |
| Protect | จำนวน Finding ด้าน Security = 0 หรือมี Plan ปิด |
| Evolve | Upgrade สำเร็จไม่เกินเวลาที่วางแผน ± 20% |
| Retire | ข้อมูล Archive ครบ 100% ตาม Retention |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตารางกิจกรรมรายสัปดาห์ของ DBA

```text
วันจันทร์
  09:00 ตรวจ Alert ที่ค้างจากวันหยุด
  09:15 ตรวจ Backup Success (pgbackrest info)
  09:30 ตรวจ XID Age และ n_dead_tup
  10:00 ตรวจ pg_stat_statements Top 5

วันพุธ
  09:00 รัน weekly_report.sql
  10:00 ประชุมทีม DevOps + Cloud Engineer

วันศุกร์
  09:00 Restore Test ผลล่าสุด
  10:00 ตรวจ Certificate วันหมดอายุ
  11:00 เตรียม Change สำหรับสัปดาห์ถัดไป
```

### ตัวอย่างที่ 2: Sequence ที่ใกล้เต็ม แสดงถึงระยะ Evolve

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

> ✅ Sequence ใช้ไป 99.92% แสดงว่าต้องเข้าสู่ระยะ **Evolve** เพื่อทำ Migration PK integer → bigint

### ตัวอย่างที่ 3: Health Check Report

```bash
sudo -u postgres PGDATABASE=gridcare TEXTFILE_DIR=/var/lib/prometheus/node-exporter ./health_check.sh
```

ผลลัพธ์:
```text
connections          OK   1/100              1.0%
idle_in_transaction  OK   0
xid_age              OK   1765
archiver             OK   failed_count=0
pg_wal_size          OK   768 MB             49 ไฟล์
index_invalid        OK   0
password_expiry      OK   -
[2026-11-04 13:00:45] สรุป: exit code 0 (OK) host=local db=gridcare
```

## 12. สรุปย่อ จำง่าย
- วงจรชีวิต = **Plan → Provision → Configure → Operate → Optimize → Protect → Evolve → Retire**  
- ทุกระยะต้องมี **Metric, Alert, Runbook**  
- ทุกระยะมี **Gate** ที่ต้องผ่านก่อนไปขั้นถัดไป  
- **Operate** คือระยะที่ใช้เวลานานที่สุด และเป็นที่เกิด Incident มากที่สุด  
- **Evolve** คือระยะที่เสี่ยงที่สุดถ้าไม่มี Rollback Plan

ประโยคจำ: **“ทุกระยะมี KPI ทุก Gate มี Evidence”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation: https://www.postgresql.org/docs/17/
- ITIL 4 Service Lifecycle
- Google SRE Book: https://sre.google/sre-book/
- GridCare Workshop: `scripts/health_check.sh`, `scripts/weekly_report.sql`, `scripts/restore_test.sh`
- Outline หลักสูตร Advanced PostgreSQL for Enterprise Production (PEA)

---

# บทที่ 5 หลักการ Monitoring และ Observability

## 1. เรื่อง
หลักการ Monitoring และ Observability ในระบบ PostgreSQL Production โดยใช้ Prometheus, Alertmanager และ Grafana

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจความแตกต่างระหว่าง Monitoring และ Observability  
2. เพื่อให้เลือก Metric ที่ตอบคำถามทางธุรกิจได้  
3. เพื่อให้เข้าใจ Prometheus, Exporter, Alertmanager ในเชิงบทบาท  
4. เพื่อให้วางแผน Dashboard และ Alert ที่ actionable

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบายความแตกต่าง Monitoring vs Observability
- อธิบาย 3 เสาหลัก (Metrics, Logs, Traces) และการใช้งานของแต่ละตัว
- อธิบาย Prometheus Pull Model, Exporter และ TSDB
- ออกแบบ Dashboard ที่ตอบคำถาม “ระบบยังดีไหม”
- ออกแบบ Alert ที่ตอบคำถาม “มีอะไรต้องทำเดี๋ยวนี้”

## 4. เนื้อหาโดยย่อ

### Monitoring vs Observability
- **Monitoring** = การเฝ้าระวัง Metric ที่รู้ล่วงหน้าว่าสำคัญ  
- **Observability** = ความสามารถในการตอบคำถามใหม่ ๆ จากข้อมูลที่มีอยู่

### 3 เสาหลัก
1. **Metrics** — ตัวเลข ไม่มี Cardinality สูง เหมาะกับ Dashboard และ Alert  
2. **Logs** — เหตุการณ์ เหมาะกับการสืบสวน  
3. **Traces** — เส้นทาง Request เหมาะกับการหา Bottleneck ในระบบ Distributed

### Prometheus
- เก็บ Metric เป็น Time-Series  
- ดึง (Pull) จาก Exporter ตาม `scrape_interval`  
- ใช้ PromQL ในการ Query  
- ใช้ Alert Rule เพื่อส่งให้ Alertmanager

### Alertmanager
- รับ Alert จาก Prometheus  
- จัดกลุ่ม (Grouping), เส้นทาง (Routing), ยับยั้ง (Inhibition)  
- ส่งอีเมล, Slack, Webhook, Pager

### หลักการออกแบบ Metric
1. Metric ต้องตอบคำถามธุรกิจหรือ SLO ได้  
2. Metric ต้องมี Label ที่ช่วยกรองได้ เช่น `datname`, `instance`, `state`  
3. Alert ต้องเป็น Actionable  
4. Dashboard ต้องเรียงจากบนลงล่าง “ภาพรวม → ปัญหา → รายละเอียด”

## 5. ประโยชน์ที่ได้รับ
- เลือก Metric ได้ตรงกับคำถาม  
- ลด Alert ที่ไม่ actionable  
- เลือกใช้ Metrics, Logs หรือ Traces ได้เหมาะกับงาน  
- ทำให้ Dashboard และ Alert ออกแบบจาก SLO ได้  
- ทำให้การตอบ Incident มีข้อมูลที่เชื่อถือได้

## 6. ข้อควรระวัง
- **Label Cardinality สูง** เช่น `query` ที่ไม่ Normalize จะทำให้ Prometheus เครียด  
- ** scrape_interval สั้นเกินไป** ทำให้โหลดระบบสูง  
- **`rate()` ต้องใช้กับ Counter เท่านั้น** ไม่ใช่ Gauge  
- **Alert ที่ไม่มี `for:`** จะทำให้เกิด False Positive บ่อย  
- **Grafana Panel ที่ใช้ `rate()` กับ Gauge** จะได้กราฟที่ไม่มีความหมาย

## 7. ข้อดี
- Prometheus + Alertmanager + Grafana เป็น Open Source ที่ใช้งานร่วมกันได้ดี  
- มี Community และ Ecosystem ที่กว้าง  
- ใช้ Pull Model ทำให้ควบคุม Load ได้  
- PromQL ยืดหยุ่นสูง

## 8. ข้อเสีย
- Prometheus ไม่เหมาะกับ Cardinality สูงมาก  
- ต้องใช้ Storage แยกสำหรับ Long-term (เช่น Thanos หรือ Mimir)  
- Exporter บางตัวต้องเขียน Query เอง  
- การออกแบบ Alert ที่ดีต้องใช้เวลาและความเข้าใจระบบ

## 9. ข้อห้าม
- ห้ามใช้ `datname` หรือ Label อะไรก็ตามที่ Cardinality สูงผิดปกติ  
- ห้ามใช้ `rate()` กับ `pg_up` หรือ Gauge อื่น  
- ห้ามตั้ง Alert ที่ไม่มี Runbook  
- ห้ามปิด Exporter เพื่อแก้ปัญหา Resource  
- ห้ามใช้ Dashboard เป็นที่เดียวของ Observability

## 10. รายละเอียด

### 10.1 ตารางเปรียบเทียบ 3 เสาหลัก

| มิติ | Metrics | Logs | Traces |
|---|---|---|---|
| ลักษณะข้อมูล | ตัวเลข | ข้อความ | เส้นทาง Request |
| Cardinality | ต่ำ-กลาง | สูง | สูง |
| ใช้กับ | Dashboard, Alert | สืบสวน | วิเคราะห์ Latency |
| เครื่องมือ | Prometheus, Grafana | Loki, ELK, pgBadger | Jaeger, Tempo |
| ข้อจำกัด | ไม่มีบริบท | ปริมาณมาก | ต้องมี Instrument |

### 10.2 สถาปัตยกรรม Prometheus

```text
PostgreSQL + Linux
   │
   ├── postgres_exporter :9187
   └── node_exporter :9100
   │
   ▼ (Pull ทุก 15s)
Prometheus :9090
   │
   ├── PromQL → Grafana :3000
   └── Alert Rule → Alertmanager :9093
                          │
                          ├── Email
                          ├── Slack
                          └── Webhook/Pager
```

### 10.3 หลักการออกแบบ Dashboard

1. **แถวที่ 1:** SLO/KPI หลัก (Availability, TPS, p95, Error Rate)  
2. **แถวที่ 2:** ทรัพยากร (CPU, Memory, Disk)  
3. **แถวที่ 3:** ฐานข้อมูล (Connection, XID, Replication, Lock)  
4. **แถวที่ 4:** Top N (Top Query, Top Table Bloat, Top Lock)  
5. **แถวที่ 5:** Alert Status และ Recent Restart

### 10.4 หลักการออกแบบ Alert

| ระดับ | ตัวอย่าง | เกณฑ์ |
|---|---|---|
| Critical | `pg_up=0`, `PatroniPrimaryCountNotOne`, `DiskFull` | Pager ทันที |
| Warning | Connection > 80%, Replication Lag > 30s | Slack/Email |
| Info | Restart, Backup Success, Config Reload | Log Only |

**ทุก Alert ต้องมี:**
- `severity`
- `summary`
- `description`
- `runbook_url`
- `for:` ที่เหมาะสม

### 10.5 ตัวอย่าง Metric ที่ควรมีใน PostgreSQL Dashboard

| Panel | PromQL | หน่วย |
|---|---|---|
| Up | `pg_up` | boolean |
| TPS | `sum by (datname) (rate(pg_stat_database_xact_commit{datname="gridcare"}[1m]) + rate(pg_stat_database_xact_rollback{datname="gridcare"}[1m]))` | ops/s |
| Connections | `sum by (state) (pg_stat_activity_count{datname="gridcare"})` | count |
| Cache Hit | `rate(pg_stat_database_blks_hit{datname="gridcare"}[5m]) / (rate(pg_stat_database_blks_hit{datname="gridcare"}[5m]) + rate(pg_stat_database_blks_read{datname="gridcare"}[5m]))` | ratio |
| XID Age | `pg_database_wraparound_age_datfrozenxid_seconds` | seconds |
| Dead Tuple | `topk(5, pg_stat_user_tables_n_dead_tup{schemaname="gridcare"})` | count |
| Replication Lag | `max by (instance, application_name) (pg_stat_replication_pg_wal_lsn_diff)` | bytes |
| WAL Size | `sum(pg_ls_waldir_size_bytes)` | bytes |
| Backup Age | `time() - gridcare_backup_last_success_timestamp_seconds` | seconds |

### 10.6 ตัวอย่าง Log-Based Observability

- PostgreSQL `log_min_duration_statement = 500ms` → ใช้ pgBadger  
- `log_lock_waits = on` → เห็น Lock Wait  
- `log_checkpoints = on` → เห็น Checkpoint  
- `auto_explain` สำหรับ Query ช้า  
- `pgaudit` สำหรับ Audit

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตั้ง Prometheus Scrape

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: postgres
    static_configs:
      - targets: ['pg1:9187', 'pg2:9187']
```

### ตัวอย่างที่ 2: Alert `PostgresDown`

```yaml
- alert: PostgresDown
  expr: pg_up == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "PostgreSQL instance {{ $labels.instance }} down"
    description: "pg_up = 0 ต่อเนื่อง 1 นาที ตรวจ process, network และ exporter"
    runbook_url: "http://gridcare-infra/runbooks/C08-postgres-down.md"
```

### ตัวอย่างที่ 3: ตรวจ Target ใน Prometheus

```bash
curl -s localhost:9090/api/v1/targets | python3 -m json.tool | grep -E '"scrapeUrl"|"health"'
```

ผลลัพธ์:
```text
"scrapeUrl": "http://pg1:9187/metrics",
"health": "up"
"scrapeUrl": "http://pg2:9187/metrics",
"health": "up"
```

### ตัวอย่างที่ 4: Dashboard TPS Panel

```promql
sum by (datname) (
  rate(pg_stat_database_xact_commit{datname="gridcare"}[1m])
  + rate(pg_stat_database_xact_rollback{datname="gridcare"}[1m])
)
```

### ตัวอย่างที่ 5: ตรวจ Alert ที่ Firing

```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

ผลลัพธ์:
```text
"alertname": "PostgresRecentlyRestarted",
"state": "firing"
```

## 12. สรุปย่อ จำง่าย
- **Monitoring** = รู้ว่ามีอะไรผิดปกติ  
- **Observability** = ตอบคำถามใหม่จากข้อมูลที่มี  
- **Metrics + Logs + Traces** คือเสาหลัก  
- **Prometheus** = Pull + TSDB + PromQL + Alert Rule  
- **Alertmanager** = จัดกลุ่ม + เส้นทาง + ส่ง  
- **Grafana** = Dashboard ที่ตอบคำถาม “ระบบยังดีไหม”  
- **Alert ที่ดี** = Actionable + Severity + Runbook + `for:`

ประโยคจำ: **“Metric ตอบว่าระบบเป็นอย่างไร Log ตอบว่าเกิดอะไร Trace ตอบว่าช้าที่ไหน”**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Prometheus Documentation: https://prometheus.io/docs/
- Alertmanager Documentation: https://prometheus.io/docs/alerting/latest/alertmanager/
- Grafana Documentation: https://grafana.com/docs/
- Google SRE Book — Monitoring Distributed Systems: https://sre.google/sre-book/monitoring-distributed-systems/
- PostgreSQL Documentation — Monitoring: https://www.postgresql.org/docs/17/monitoring.html
- GridCare Workshop Day 2: Lab 3.1, Lab 3.2 และ Day 4: Lab 4.1

---

## สรุปส่วนที่ 1 (บทที่ 2–5)

| บท | แก่นของบท | บทถัดไป |
|---|---|---|
| 2 | บทบาทและ RACI ของ DevOps / Cloud / DBA | 3 สถาปัตยกรรม |
| 3 | Process, Storage, WAL, MVCC และ Metric ที่ผูกกับสถาปัตยกรรม | 4 วงจรชีวิต |
| 4 | 8 ระยะของวงจรชีวิต + Gate + KPI | 5 Monitoring |
| 5 | Monitoring vs Observability, Prometheus, Alertmanager, Grafana | 6 Prometheus เชิงลึก |

 