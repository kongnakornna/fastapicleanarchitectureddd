# 📋 คัมภีร์วิศวกรรมฐานข้อมูล PostgreSQL ระดับ Enterprise Production
> **หลักสูตร:** Advanced PostgreSQL for Enterprise Production (PEA)
> **ระบบอ้างอิง:** GridCare Database System Cluster (PostgreSQL 18 + Patroni + Prometheus)
> **สถานะเอกสาร:** RELEASED (เวอร์ชันใช้งานจริงบน Production)

---

## 📊 ส่วนที่ 1: สถาปัตยกรรมทางเดินข้อมูลและระบบ Observability
พิมพ์เขียวร้อยเรียงระบบข้อมูล (Data Flow), ระบบสถิติ (Metric Flow) และสัญญาณเตือนภัย (Alert Flow) ขององค์กร:

```text
[ชั้นแอปพลิเคชัน / ลูกข่าย API]
         │
         ▼
[PgBouncer :6432]  ◄── บริหารจัดการ Connection Pool ลด Overhead ทราฟฟิกพุ่งสะดุด
         │
         ▼
[HAProxy :5000 / :5001] ◄── สแกนตรวจสุขภาพแยกโหนดเขียนโหนดอ่านผ่าน REST API พอร์ต 8008
         │
 ┌───────┴────────────────────────────┐
 │ (ทางเดินข้อมูลหลัก: โหนดเขียน)      │ (ทางเดินข้อมูลรอง: โหนดอ่าน)
 ▼                                    ▼
[pg1: Primary PostgreSQL 18]        [pg2: Replica PostgreSQL 18]
 │       │                                    ▲
 │       ├──────(Replication Flow: Wal Slots)─┘  *(ทำ pg_rewind อัตโนมัติลด Split-Brain)
 │       │
 │       ├──► [node_exporter :9100] ───────► แปลง Metric ของ OS (CPU, RAM, Disk, Network)
 │       ├──► [postgres_exporter :9187] ───► แปลง Metric ของ Engine (TPS, Locks, Cache Hit)
 │       └──► [Patroni REST API :8008] ─────► แปลง Metric ของ HA Cluster (State, Timeline)
 │                                                       ▲
 └───(Backup Flow: pgBackRest + S3 API HTTPS)           │ (Scrape HTTP Pull ทุก 15 วินาที)
         │                                               │
         ▼                                     [ เซิร์ฟเวอร์มอนิเตอร์ส่วนกลาง: infra ]
[infra: MinIO / Object Storage]                          │
   (จัดเก็บไฟล์ Full/Diff/Incr Backup                    ▼
    และไฟล์ WAL Archive ทุก 60 วินาที)          [Prometheus Server :9090] ◄── ประมวลผล Alert Rules
                                                         │
                                                         ▼ (ส่งมอบโครงสร้าง JSON Payload)
                                                [Alertmanager :9093] ──────► กรองตัวซ้ำ / จัดเส้นทาง
                                                         │
                                                         ▼
                                                [Mailpit / Slack / PagerDuty] ──► เปิดลิงก์ Runbook URL
```

---

## 🛠️ ส่วนที่ 2: สรุปชุดคำสั่งสำคัญเชิงวิศวกรรม (5 มิติโครงสร้าง)

### 1. คำสั่งสร้าง Extended Statistics (Day 2)
* **เรื่อง:** การสร้างสถิติความสัมพันธ์ระหว่างคอลัมน์ (Extended Statistics) เพื่อเพิ่มความแม่นยำให้ Query Planner
* **วัตถุประสงค์:** แก้ไขปัญหา Query Planner ประมาณจำนวนแถวผิดพลาด (Row Estimate Mismatch) ส่งผลให้เปลี่ยนจาก Index Scan ความเร็วสูง เป็น Parallel Seq Scan ช้าๆ ที่กินทรัพยากรระบบมหาศาล
* **คืออะไร:** เครื่องมือบอกใบ้สถิติเชิงลึกแก่ PostgreSQL ให้รับรู้ว่าข้อมูลใน 2 คอลัมน์ขึ้นไปมีความสัมพันธ์เกี่ยวเนื่องกัน
* **ทำงานอย่างไร:** บันทึกโครงสร้างสถิติลงในระบบแคตตาล็อก `pg_statistic_ext` เมื่อรันคำสั่ง `ANALYZE` ระบบจะสร้างตารางความถี่ร่วมกัน (MCV Matrix) เก็บไว้
* **เพื่ออะไร:** ลดเวลาประมวลผล (Execution Time) ของคำสั่งที่มีเงื่อนไขซับซ้อนหลายคอลัมน์จากหลักร้อยมิลลิวินาทีให้เหลือต่ำกว่า 1 มิลลิวินาที
* **คำสั่งใช้งาน:**
  ```sql
  CREATE STATISTICS gridcare.bills_period_status (mcv) ON billing_period, status FROM gridcare.bills;
  ANALYZE gridcare.bills;
  ```

### 2. คำสั่งตรวจสอบหัวคิวล็อก Root Blocker (Day 1, 2, 5)
* **เรื่อง:** การตรวจหาและระบุหมายเลข Process (PID) ที่เป็นต้นตอทำลายระบบล็อก (Lock Queue Bloat)
* **วัตถุประสงค์:** ตัดวงจรปัญหาระบบค้าง (Application Stalled) จากการติดล็อกค้างสะสม โดยระบุ Session ต้นตอเพื่อสั่งยกเลิกงานได้อย่างแม่นยำ ไม่ทำลายเซสชันผู้ใช้ทั่วไป
* **คืออะไร:** คำสั่งสืบค้นระบบแคตตาล็อก `pg_stat_activity` ร่วมกับฟังก์ชัน `pg_blocking_pids` เพื่อหาตัวแปรที่กำลังขวางเพื่อนอยู่
* **ทำงานอย่างไร:** กรองหาแถวที่มีคนรอคิวล็อกอยู่ แต่ตัวมันเองไม่มีรหัสใดขวางอยู่ด้านหลัง (Array ว่าง `{}`)
* **คำสั่งใช้งาน:**
  ```sql
  SELECT pid, usename, state, clock_timestamp() - xact_start AS xact_age, pg_blocking_pids(pid) AS blocked_by, left(regexp_replace(query, '\s+', ' ', 'g'), 60) AS root_query
  FROM pg_stat_activity 
  WHERE state <> 'idle' AND (pg_blocking_pids(pid) <> '{}' OR pid IN (SELECT unnest(pg_blocking_pids(p)) FROM pg_stat_activity p))
  ORDER BY xact_age DESC;
  ```
* **คำสั่งจัดการต่อจาก Runbook:**
  ```sql
  SELECT pg_cancel_backend(<PID>);    -- ขั้นเบา: ยกเลิกเฉพาะคิวงานรันค้าง
  SELECT pg_terminate_backend(<PID>); -- ขั้นเด็ดขาด: ตัดการเชื่อมต่อเซสชันทันที
  ```

### 3. คำสั่งสำรองข้อมูล Directory Parallel + zstd (Day 3)
* **เรื่อง:** การ Dump สำรองฐานข้อมูลขนาดใหญ่แบบแยกโฟลเดอร์ขนานพร้อมบีบอัดระดับสูง
* **วัตถุประสงค์:** ลดระยะเวลาการทำ Backup Window บนระบบ Production และลดขนาดพื้นที่จัดเก็บไฟล์สำรองข้อมูล (Storage Optimization)
* **คืออะไร:** คำสั่งรันผ่านยูทิลิตี้ `pg_dump` โหมด Directory ร่วมกับอัลกอริทึมบีบอัดความเร็วสูง `zstd`
* **ทำงานอย่างไร:** สร้าง Worker Thread แยกย่อยตามจำนวนจ็อบ วิ่งเข้าไปดึงข้อมูลจากตารางต่าง ๆ ออกมาเขียนลงดิสก์พร้อมกันแบบ Real-time
* **คำสั่งใช้งาน:**
  ```bash
  time sudo -u postgres pg_dump -d gridcare -Fd -j 2 -Z zstd:3 -f /var/backups/gridcare/gc.dir
  ```

### 4. คำสั่งกู้คืนข้อมูล Point-in-Time Recovery: PITR (Day 3, 4, 5)
* **เรื่อง:** การทำแท่นกู้ภัยข้อมูลย้อนหลังกลับสู่จุดเวลาวินาทีก่อนเกิดภัยพิบัติ
* **วัตถุประสงค์:** กู้คืนระบบฐานข้อมูลกรณีข้อมูลเสียหายรุนแรงจากแอปพลิเคชันหรือมนุษย์ ให้กลับมาทำงานได้โดยสูญเสียข้อมูลน้อยที่สุด (RPO ต่ำที่สุด)
* **คืออะไร:** กระบวนการสั่งเครื่องมือ `pgbackrest` ให้ทำการ Restore ไฟล์ข้อมูลชุดหลัก (Base Backup) จาก S3 Repository ร่วมกับคอนฟิกเวลาเป้าหมาย
* **ทำงานอย่างไร:** ระบบจะดึงไฟล์ WAL Archive จาก S3 (MinIO) มาทำ Redo Log ย้อนหลังไล่เวลาขึ้นมาจนถึงวินาทีที่กำหนด และจะสลับ Timeline ID ทันทีเพื่อป้องกันการเขียนข้อมูลทับเส้นเวลาเก่า
* **คำสั่งใช้งาน:**
  ```bash
  sudo systemctl stop postgresql@18-main
  TARGET="2026-11-04 14:51:12+07"
  sudo -u postgres pgbackrest --stanza=gridcare --delta --type=time --target="$TARGET" --target-action=promote restore
  sudo systemctl start postgresql@18-main
  ```

### 5. คำสั่งซ้อมจำลองเครือข่ายขาด DCS Split-Brain ด้วย iptables (Day 4)
* **เรื่อง:** การบล็อกทราฟฟิกระหว่างโหนดคลัสเตอร์เพื่อทดสอบกลไก High Availability (Patroni/etcd)
* **วัตถุประสงค์:** ตรวจสอบและยืนยันว่าระบบจะไม่เกิดปัญหา Split-Brain (โหนดสองตัวคิดว่าเป็นตัวเขียนทั้งคู่) และระบบแอปพลิเคชันสามารถสลับเส้นทางไปหาโหนดใหม่ได้โดยไม่สะดุด
* **คืออะไร:** การใช้คำสั่งควบคุมระดับ Kernel Network (`iptables`) บล็อกช่องทางการสื่อสารของโหนด Primary เพื่อจำลองสถานการณ์พายุเข้าหรือเครือข่ายขาด
* **คำสั่งใช้งาน (สั่งบล็อก):**
  ```bash
  sudo iptables -I INPUT 1 -s 10.104.0.12 -j DROP
  sudo iptables -I INPUT 1 -s 10.104.0.13 -j DROP
  sudo iptables -I OUTPUT 1 -d 10.104.0.12 -j DROP
  sudo iptables -I OUTPUT 1 -d 10.104.0.13 -j DROP
  ```
* **คำสั่งใช้งาน (ปลดบล็อกหลังซ้อมเสร็จ):**
  ```bash
  sudo iptables -D INPUT -s 10.104.0.12 -j DROP
  sudo iptables -D INPUT -s 10.104.0.13 -j DROP
  sudo iptables -D OUTPUT -d 10.104.0.12 -j DROP
  sudo iptables -D OUTPUT -d 10.104.0.13 -j DROP
  ```

### 6. คำสั่งรันตรวจสอบ Safe Migration ผ่านตัวควบคุม (Day 5)
* **เรื่อง:** การ Deploy โครงสร้างฐานข้อมูล (Schema Change) ผ่านสคริปต์ควบคุมความปลอดภัยระดับคิวล็อก
* **วัตถุประสงค์:** ป้องกันเหตุการณ์ Migration ทำระบบล่มเนื่องจากคำสั่งปรับโครงสร้างตารางมักขอสิทธิ์ล็อกระดับ Access Exclusive Lock ซึ่งจะบล็อกทุกทราฟฟิกหากเกิดคิวสะสม
* **คืออะไร:** การทำงานของสคริปต์ควบคุม `run_migration.sh` ที่บังคับควบคุมค่าพารามิเตอร์ `lock_timeout` ให้ต่ำ หากไม่สอดคล้องจะถอยออก (Abort) แล้วรันซ้ำอัตโนมัติ (Retry Loop)
* **คำสั่งใช้งาน:**
  ```bash
  sudo -u postgres PGDATABASE=gridcare /opt/gridcare/scripts/run_migration.sh /var/tmp/migrations/m2a_add_constraints.sql
  ```

### 7. คำสั่งตรวจสอบความพร้อมก่อนอัปเกรดเวอร์ชัน pg_upgrade --check (Day 5)
* **เรื่อง:** การตรวจสอบความเข้ากันได้ของโครงสร้างแคตตาล็อกก่อนรัน Major Upgrade
* **วัตถุประสงค์:** ลดความเสี่ยงของการอัปเกรดเวอร์ชันฐานข้อมูลหลักพังกลางคัน ซึ่งอาจทำให้ไฟล์ข้อมูลเสียหายถาวร
* **คืออะไร:** โหมดทดสอบจำลอง (Dry-run mode) ของโปรแกรม `pg_upgrade` เพื่อตรวจสอบความพร้อมก่อนรันย้ายลิงก์ไฟล์ข้อมูลจริง (`--link`)
* **คำสั่งใช้งาน:**
  ```bash
  cd /var/lib/postgresql
  sudo -u postgres /usr/lib/postgresql/18/bin/pg_upgrade --check -b /usr/lib/postgresql/17/bin -B /usr/lib/postgresql/18/bin -d /var/lib/postgresql/17/main -D /var/lib/postgresql/18/main -o "-c config_file=/etc/postgresql/17/main/postgresql.conf" -O "-c config_file=/etc/postgresql/18/main/postgresql.conf"
  ```

### 8. คำสั่งพยากรณ์พื้นที่ดิสก์ล่วงหน้า predict_linear (Day 2, 4, 5)
* **เรื่อง:** การเขียนสูตรคำนวณ PromQL บนมอนิเตอร์เพื่อทำนายอนาคตทรัพยากรดิสก์
* **วัตถุประสงค์:** เปลี่ยนระบบมอนิเตอร์จากการตั้งรับ (Reactive) ให้เป็นการบริหารจัดการเชิงรุก (Proactive Capacity Planning) เพื่อขยายพื้นที่จัดเก็บข้อมูลล่วงหน้าก่อนดิสก์เต็มจริงจนระบบฐานข้อมูลพังชะงัก
* **คืออะไร:** ฟังก์ชันคำนวณทางคณิตศาสตร์แบบประมาณค่าเชิงเส้น (Linear Regression) บน Prometheus
* **สูตรคำสั่ง PromQL สำหรับแท่นแจ้งเตือน:**
  ```promql
  predict_linear(node_filesystem_free_bytes{mountpoint="/"}[7d], 30 * 86400) < 0
  ```

---

## 📋 ส่วนที่ 3: แพลตฟอร์มแม่แบบมาตรฐานพร้อมใช้งาน (Templates)

### 1. คู่มือปฏิบัติการแก้ไขปัญหาด่วน (Operational Runbook Template)
*   **ลิงก์ไฟล์อ้างอิง:** `http://gridcare-infra/runbooks/C01-lock-timeout-queues.md`

```markdown
# 📋 RUNBOOK CODE: C01-LOCK-TIMEOUT-QUEUES
**ชื่ออุบัติการณ์:** เกิดคิวล็อกสะสมตัวหนาแน่น (Lock Queue Bloat)
**ระดับความรุนแรง:** 🔴 CRITICAL
**ทีมผู้รับผิดชอบหลัก:** Database Administrator (DBA) & DevOps Team

---

## 🔍 1. ขั้นตอนการตรวจสอบและวินิจฉัย (Diagnosis Steps)
เข้าเครื่อง `pg1` แล้วรันคำสั่ง SQL ด้านล่างนี้ทันทีเพื่อหาหัวคิวล็อก (Root Blocker PID):
```sql
SELECT pid, usename, clock_timestamp() - xact_start AS xact_age, pg_blocking_pids(pid) AS blocked_by, wait_event_type, wait_event, left(query, 100) AS short_query
FROM pg_stat_activity 
WHERE state <> 'idle' AND (pg_blocking_pids(pid) <> '{}' OR pid IN (SELECT unnest(pg_blocking_pids(p)) FROM pg_stat_activity p))
ORDER BY xact_age DESC;
```
**เกณฑ์การตัดสินใจ (Decision Criteria):**
* หากพบ Session ที่มี `xact_age` เกิน 5 นาที และค่า `blocked_by` เป็นช่องว่าง `{}` แสดงว่าตารางนั้นคือ **หัวคิวล็อก (Root Blocker PID)**

---

## 🛠️ 2. ขั้นตอนการแก้ไขปัญหา (Resolution Steps)
### ขั้นที่ 2.1: ส่งสัญญาณยุติคำสั่งแบบนุ่มนวล (Cancel Query)
```sql
SELECT pg_cancel_backend(<ROOT_BLOCKER_PID>);
```
*รอเวลา 10 วินาที หากเซสชันหัวคิวยังไม่ยอมออก ให้ยกระดับขั้นถัดไป*

### ขั้นที่ 2.2: สั่งตัดการเชื่อมต่อขั้นเด็ดขาด (Terminate Session)
```sql
SELECT pg_terminate_backend(<ROOT_BLOCKER_PID>);
```

---

## ✅ 3. ขั้นตอนการตรวจสอบยืนยันหลังกู้ระบบ (Verification Steps)
รันคำสั่งตรวจนับจำนวนคิวล็อกค้างเพื่อตรวจสอบว่าตัวเลขกลับสู่สภาวะปกติจริง:
```sql
SELECT count(*) FROM pg_stat_activity WHERE pg_blocking_pids(pid) <> '{}';
```
*ผลลัพธ์ที่ยอมรับได้: ตัวเลขต้องเป็น `0` และกราฟ TPS บน Grafana ต้องเด้งกลับมาขึ้นระดับปกติ*

---

## 🔙 4. แผนงานการคืนสภาพระบบกรณีฉุกเฉิน (Rollback Plan)
หากการทำ Terminate Session ส่งผลกระทบเป็นวงกว้าง ให้สั่งรีสตาร์ตหน่วย Connection Pooler:
```bash
sudo systemctl restart pgbouncer
```
```

### 2. ฟอร์มบันทึกข้อมูลอุบัติการณ์สรุปหน้าเดียว (Incident Record Template)

```markdown
# 📑 INCIDENT RECORD REPORT
**Incident ID:** INC-2026-1105  
**ระดับความรุนแรง:** 🔴 CRITICAL (Severity 1)  
**ชื่อเหตุการณ์:** ฐานข้อมูลโหนดหลักหยุดทำงานและเกิดระบบสลับคลัสเตอร์อัตโนมัติ  
**ระบบที่ได้รับผลกระทบ:** ระบบรับชำระค่าไฟฐานข้อมูล GridCare  

---

## 📊 1. ตัวชี้วัดสำคัญเชิงปฏิบัติการ (Key Operational Metrics)
*   **เวลาเริ่มต้นเกิดเหตุ (T0):** 2026-11-05 14:30:15 ICT  
*   **เวลาที่กู้คืนระบบสำเร็จ (T2/Mitigated):** 2026-11-05 14:30:46 ICT  
*   **ระยะเวลา Downtime รวม:** 31.3 วินาที  
*   **ค่า RTO ที่เกิดขึ้นจริง (Actual RTO):** **31.3 วินาที** (เป้าหมายตาม SMART Goal: ≤ 45 วินาที)  
*   **ค่า RPO ที่เกิดขึ้นจริง (Actual RPO):** **0 รายการ** (ไม่มีข้อมูลยืนยันธุรกรรมสูญหายเนื่องจากใช้ระบบ Replication Slots)  
*   **จำนวนธุรกรรมที่เสียหายชั่วคราว (Failed Transactions):** pgbench failed transactions = 234 รายการ  

---

## 📝 2. ลำดับเหตุการณ์โดยย่อ (Executive Summary)
เมื่อวันที่ 5 พฤศจิกายน 2569 เวลา 14:30:15 น. เกิดเหตุการณ์โหนด Primary เดิม (pg1) หลุดออกจากระบบเครือข่ายส่งผลให้กระบวนการเขียนข้อมูลชะงักทันที ระบบ Monitoring ตรวจพบสัญญาณผิดปกติและแจ้งเตือนผ่านกฎ "PostgresDown" ภายในเวลา 31.3 วินาที ระบบ Patroni คลัสเตอร์ทำหน้าที่ตัดการทำงานและ Promote โหนดสำรอง (pg2) ขึ้นเป็น Leader ตัวใหม่สำเร็จ โดยมี HAProxy และ PgBouncer ทำการสลับช่องทางทราฟฟิกของแอปพลิเคชันตามไปทันทีโดยไม่ต้องแก้ไขโค้ด ทำให้ระบบชำระเงินกลับมาทำงานได้ตามปกติ

---

## 🛠️ 3. มาตรการกู้ภัยและยืนยันผล (Mitigation & Validation)
1.  **การแก้ไขเบื้องต้น:** ปล่อยระบบ Patroni ทำการเลือกตั้งผู้นำโหนดใหม่แบบอัตโนมัติ และ On-call เข้าตรวจสอบ Log คลัสเตอร์ผ่านคำสั่ง `patronictl list`
2.  **การยืนยันความสมบูรณ์ข้อมูล:** รันสคริปต์สืบค้นยอดรวมการรับชำระเงินยืนยันเลข ID ล่าสุดระดมตรวจเปรียบเทียบระหว่าง `ok_ids.txt` และ `db_ids.txt` พบค่า RPO = 0 สอดคล้องกันสมบูรณ์

---

## 📋 4. ลิงก์เอกสารอ้างอิงและบันทึกเพิ่มเติม (References)
*   **ลิงก์รายงานผลการวิเคราะห์สาเหตุเชิงลึก (RCA/PSR):** `http://wiki.internal`
*   **บันทึก Log ไฟล์แนบ:** `postgresql-18-main.log` ช่วงเวลา 14:30:00 ถึง 14:35:00
```

---

## 📈 ส่วนที่ 4: ตัวชี้วัดสากลและแผนการดำเนินงานต่อเนื่อง (KPI & SMART)

### 1. ตารางเปรียบเทียบผลลัพธ์สำคัญ (Enterprise KPI Metrics)
ดัชนีชี้วัดที่เกิดขึ้นจริงจากการใช้งานชุดคำสั่งเชิงรุกในหลักสูตร 5 วัน:

| กิจกรรม / ตัวชี้วัด | สถานะเดิม (ก่อนปรับแต่ง) | สถานะใหม่ (หลังใช้คำสั่งเชิงรุก) | ผลลัพธ์เชิงวิศวกรรม |
|---|---|---|---|
| **ความเร็วการค้นหาข้อมูลไฟ (Q1)** | 45.789 ms (Seq Scan ช้า) | **0.067 ms** (Index Scan ด่วน) | **เร็วขึ้น 683 เท่า** 🚀 |
| **การประมวลผลหน้ารายการชำระเงิน (Q3)** | 234.789 ms (Sort ล้นลงดิสก์) | **0.256 ms** (Keyset Pagination) | **เร็วขึ้น 917 เท่า** และลด Disk I/O 📉 |
| **ธุรกรรมรวมของระบบ (Throughput)** | 93 tps (ต่อตรงฐานข้อมูล) | **149 tps** (ผ่านการจูนแคช Pooler) | **ประสิทธิภาพระบบเพิ่มขึ้น +60%** |
| **ระยะเวลากู้ภัยระบบล่ม (Failover RTO)** | > 8 นาที (วิศวกรไล่เปิดมือทีละเครื่อง) | **31.3 วินาที** (Patroni ทำงานอัตโนมัติ) | **ลดระยะเวลาระบบหยุดชะงักลง 15 เท่า** |
| **สัดส่วนข้อมูลสูญหาย (Actual RPO)** | ข้อมูลสูญหายตามรอบการสำรองข้อมูล | **0 รายการ** (Replication Slot สมบูรณ์) | **ข้อมูลธุรกิจปลอดภัย 100% ไม่สูญหาย** |
| **ขั้นตอนการสลับโหนดตามแผน** | ระบบต้องหยุดทำงานชั่วคราว | **3 วินาที** (Zero failed transactions) | **ทำ Maintenance ประจำไตรมาสได้ไร้รอยต่อ** |

### 2. แผนการดำเนินงานเร่งด่วน 30 วันหลังอบรม (30-Day Action Plan)
*   **สัปดาห์ที่ 1: ตรวจความเสี่ยงเชิงลึก (Discovery & Health Check)**
    *   *งาน:* นำสคริปต์ `health_check.sh` และ `weekly_report.sql` เข้าไปรันโหมด Read-Only บนระบบองค์กร เพื่อหาจุดเสี่ยงวิกฤต เช่น ดัชนีเสีย (Invalid Index), ดัชนีซ้ำซ้อน หรือคิวล็อกที่ค้างนานเกินกำหนด
*   **สัปดาห์ที่ 2: วางแท่นระบบเก็บสถิติ (Observability Base)**
    *   *งาน:* ติดตั้ง `node_exporter` และ `postgres_exporter` บนเครื่องเซิร์ฟเวอร์ฐานข้อมูลจริง พร้อมโหลดไฟล์แดชบอร์ด `gridcare-postgres-dashboard.json` เข้าสู่ระบบ Grafana ของบริษัท
*   **สัปดาห์ที่ 3: เปิดระบบแจ้งเตือนและซ้อมกู้ข้อมูล (Alerting & PITR Test)**
    *   *งาน:* นำชุด Alert Rules ทั้ง 23 กฎเข้าสู่ระบบ Prometheus เพื่อเปิดการแจ้งเตือนหา Slack/Email ของทีม On-call พร้อมรันสคริปต์ `restore_test.sh` บนเครื่องจำลอง เพื่อบันทึกค่า RTO/RPO จริงจากไฟล์สำรองปัจจุบัน
*   **สัปดาห์ที่ 4: การซ้อมใหญ่และสร้างกลไกยั่งยืน (Game Day & Continuous Improvement)**
    *   *งาน:* จัดกิจกรรม Game Day ซ้อมจำลองสถานการณ์วิกฤต (เช่น ซ้อมทำ Patroni Switchover ช่วงทราฟฟิกต่ำ) พร้อมบรรจุฟอร์มเอกสาร RCA และ PSR เป็นมาตรฐานปฏิบัติงานประจำแผนกเมื่อเกิดเหตุระบบล่มในอนาคต

---
*Disclaimer: เอกสารนี้จัดทำขึ้นเพื่อใช้เป็นคู่มือวิศวกรรมฐานข้อมูล PostgreSQL ระดับ Enterprise Production บนระบบจำลอง GridCare ห้ามเผยแพร่ข้อมูลออกสู่สาธารณะภายนอกระบบแล็บปฏิบัติการ*