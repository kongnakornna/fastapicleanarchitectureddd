# บทที่ 71–80

> หนังสือ: คู่มือการใช้งาน PostgreSQL สำหรับ DevOps Engineer, Cloud Engineer และ DBA  
> ส่วนที่ 8 HA และ Replication  
> โทน: ทางการ กระชับ เน้นใช้งานจริง

---

# บทที่ 71 Streaming Replication

## 1. เรื่อง
Streaming Replication ใน PostgreSQL สำหรับ High Availability และ Read Scaling

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Streaming Replication  
2. เพื่อให้ตั้งค่า Primary/Replica  
3. เพื่อให้ตรวจสอบ Replication Lag  
4. เพื่อให้ใช้ Synchronous Replication

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตั้ง `wal_level = replica` และ `max_wal_senders`  
- สร้าง Replica ด้วย `pg_basebackup`  
- ตรวจสอบ `pg_stat_replication`  
- ตั้ง Synchronous Replication

## 4. เนื้อหาโดยย่อ
**Streaming Replication** = การส่ง WAL จาก Primary ไป Replica แบบ Real-time  
- Primary: `wal_level = replica`, `max_wal_senders`, `max_replication_slots`  
- Replica: `primary_conninfo`, `hot_standby = on`  
- Synchronous: `synchronous_standby_names`, `synchronous_commit`

## 5. ประโยชน์ที่ได้รับ
- HA  
- Read Scaling  
- ลด Downtime  
- RPO = 0 (Sync)

## 6. ข้อควรระวัง
- **`wal_level` ต้องตั้งก่อนสร้าง Replica**  
- **Replication Slot ต้องมี `max_slot_wal_keep_size`**  
- **Synchronous Replication ทำให้ Write ช้า**  
- **`hot_standby_feedback` อาจทำให้ Bloat**  
- **Replica ต้องมี Disk เพียงพอ**

## 7. ข้อดี
- Real-time  
- รองรับ Read Scaling  
- รองรับ HA  
- Sync ได้

## 8. ข้อเสีย
- ต้องตั้งค่า  
- Sync ทำให้ช้า  
- Replica ต้องมี Resource

## 9. ข้อห้าม
- ห้าม `wal_level = minimal` ถ้าต้องการ Replication  
- ห้ามไม่มี `max_slot_wal_keep_size`  
- ห้าม Sync Replication ที่ไม่มี Quorum  
- ห้าม Replica ที่ Disk ไม่พอ  
- ห้าม Replication ที่ไม่มี Monitoring

## 10. รายละเอียด

### 10.1 Primary Config

```ini
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
wal_keep_size = 1GB
```

### 10.2 สร้าง Role Replication

```sql
CREATE ROLE replicator WITH LOGIN REPLICATION PASSWORD 'Lab-Repl-2569';
```

### 10.3 `pg_hba.conf` สำหรับ Replication

```text
hostssl replication replicator 10.104.0.12/32 scram-sha-256
hostssl replication replicator 10.104.0.11/32 scram-sha-256
```

### 10.4 สร้าง Replica

```bash
sudo systemctl stop postgresql@17-main
sudo -u postgres rm -rf /var/lib/postgresql/17/main/*
sudo -u postgres pg_basebackup \
  -h pg1 -U replicator -D /var/lib/postgresql/17/main \
  -X stream -R -C -S pg2
sudo systemctl start postgresql@17-main
```

### 10.5 ตรวจสอบ

```sql
SELECT application_name, state, sync_state,
       write_lag, flush_lag, replay_lag,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS replay_gap
FROM pg_stat_replication;
```

ผลลัพธ์:
```text
 application_name |   state   | sync_state |    write_lag    |    flush_lag    |   replay_lag    | replay_gap 
------------------+-----------+------------+-----------------+-----------------+-----------------+------------
 pg2              | streaming | async      | 00:00:00.000088 | 00:00:00.000088 | 00:00:00.000088 | 0 bytes
```

### 10.6 Synchronous Replication

**บน Primary:**
```sql
ALTER SYSTEM SET synchronous_standby_names = 'pg2';
ALTER SYSTEM SET synchronous_commit = 'on';
SELECT pg_reload_conf();
```

ผลลัพธ์:
```text
ALTER SYSTEM
ALTER SYSTEM
 pg_reload_conf 
----------------
 t
```

### 10.7 ตรวจสอบ Sync

```sql
SELECT application_name, state, sync_state FROM pg_stat_replication;
```

ผลลัพธ์:
```text
 application_name |   state   | sync_state 
------------------+-----------+------------
 pg2              | streaming | sync
```

### 10.8 Read from Replica

```sql
-- บน pg2
SELECT pg_is_in_recovery();
```

ผลลัพธ์:
```text
 pg_is_in_recovery 
-------------------
 t
```

```sql
SELECT count(*) FROM gridcare.customers;
```

> ✅ Replica อ่านได้ (Read-only)

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตั้งค่า Primary

```ini
# /etc/postgresql/17/main/conf.d/40-gridcare-repl.conf
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
wal_keep_size = 1GB
```

### ตัวอย่างที่ 2: สร้าง Replica ด้วย `pg_basebackup`

```bash
sudo -u postgres pg_basebackup \
  -h pg1 -U replicator -D /var/lib/postgresql/17/main \
  -X stream -R -C -S pg2
```

ผลลัพธ์:
```text
pg_basebackup: initiating base backup, waiting for checkpoint to complete
pg_basebackup: checkpoint completed
pg_basebackup: write-ahead log start point: 0/2000028 on timeline 1
pg_basebackup: base backup completed
```

### ตัวอย่างที่ 3: ตรวจสอบ Replication

```sql
SELECT application_name, state, sync_state,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS replay_gap
FROM pg_stat_replication;
```

ผลลัพธ์:
```text
 application_name |   state   | sync_state | replay_gap 
------------------+-----------+------------+------------
 pg2              | streaming | async      | 0 bytes
```

### ตัวอย่างที่ 4: Sync Replication

```sql
ALTER SYSTEM SET synchronous_standby_names = 'pg2';
ALTER SYSTEM SET synchronous_commit = 'on';
SELECT pg_reload_conf();
```

### ตัวอย่างที่ 5: ตรวจสอบว่าเป็น Sync

```sql
SELECT application_name, sync_state FROM pg_stat_replication;
```

ผลลัพธ์:
```text
 application_name | sync_state 
------------------+------------
 pg2              | sync
```

## 12. สรุปย่อ จำง่าย
- **Streaming Replication = ส่ง WAL Real-time**  
- **Primary: `wal_level = replica`, `max_wal_senders`**  
- **Replica: `primary_conninfo`, `hot_standby = on`**  
- **`pg_basebackup -R -C -S`** สร้าง Replica  
- **Sync: `synchronous_standby_names`**  
- **ตรวจด้วย `pg_stat_replication`**

ประโยคจำ: **"Streaming Replication ที่ดีคือ Replication ที่ Lag 0 และ Monitor ครบ"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Log-Shipping Standby Servers: https://www.postgresql.org/docs/17/warm-standby.html
- PostgreSQL Documentation — pg_basebackup: https://www.postgresql.org/docs/17/app-pgbasebackup.html
- GridCare Workshop Day 4: Lab 2.2

---

# บทที่ 72 Replication Slots

## 1. เรื่อง
Replication Slots ใน PostgreSQL สำหรับรับประกันว่า WAL จะถูกส่งถึง Replica

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Physical และ Logical Slot  
2. เพื่อให้สร้างและตรวจสอบ Slot  
3. เพื่อให้ตั้ง `max_slot_wal_keep_size`  
4. เพื่อให้แก้ไข Slot ที่ค้าง

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- สร้าง Physical Slot  
- ตรวจสอบ `pg_replication_slots`  
- ตั้ง `max_slot_wal_keep_size`  
- ลบ Slot ที่ไม่ใช้

## 4. เนื้อหาโดยย่อ
**Replication Slot** = ตัวเก็บสถานะการส่ง WAL  
- **Physical Slot** — สำหรับ Streaming Replication  
- **Logical Slot** — สำหรับ Logical Replication

Slot รับประกันว่า WAL จะไม่ถูกลบก่อนถึง Replica  
แต่ถ้า Slot ค้าง WAL จะบวม

## 5. ประโยชน์ที่ได้รับ
- WAL ไม่หาย  
- Replica ไม่ต้อง Re-sync  
- PITR ปลอดภัยขึ้น

## 6. ข้อควรระวัง
- **Slot ค้างทำให้ WAL บวม**  
- **`max_slot_wal_keep_size` ต้องตั้ง**  
- **Slot ที่ไม่ใช้ต้องลบ**  
- **Logical Slot ทำให้ Bloat**  
- **Slot ที่ Inactive ต้องตรวจ**

## 7. ข้อดี
- WAL ไม่หาย  
- Replica ไม่ Re-sync  
- PITR ปลอดภัย

## 8. ข้อเสีย
- WAL บวมถ้า Slot ค้าง  
- ต้องดูแล

## 9. ข้อห้าม
- ห้ามลบ Slot ที่ Replica ใช้  
- ห้ามปล่อย Slot Inactive > 1 ชั่วโมง  
- ห้าม `max_slot_wal_keep_size = -1` (Unlimited)  
- ห้ามสร้าง Slot ซ้ำ  
- ห้ามใช้ Slot แทน Backup

## 10. รายละเอียด

### 10.1 ตรวจสอบ Slot

```sql
SELECT slot_name, slot_type, active, wal_status,
       pg_size_pretty(safe_wal_size) AS safe_wal_size,
       restart_lsn
FROM pg_replication_slots;
```

ผลลัพธ์:
```text
 slot_name | slot_type | active | wal_status | safe_wal_size | restart_lsn 
-----------+-----------+--------+------------+---------------+-------------
 pg2       | physical  | t      | reserved   | 10 GB         | 0/170000D8
```

### 10.2 สร้าง Physical Slot

```sql
SELECT pg_create_physical_replication_slot('pg2');
```

ผลลัพธ์:
```text
 pg_create_physical_replication_slot 
--------------------------------------
 (pg2,)
(1 row)
```

### 10.3 ตั้ง `max_slot_wal_keep_size`

```ini
max_slot_wal_keep_size = 10GB
```

> ✅ Slot จะไม่เก็บ WAL เกิน 10 GB

### 10.4 ตรวจสอบ WAL ที่ Slot เก็บ

```sql
SELECT slot_name,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_wal
FROM pg_replication_slots;
```

ผลลัพธ์:
```text
 slot_name | retained_wal 
-----------+--------------
 pg2       | 512 MB
```

### 10.5 ลบ Slot ที่ไม่ใช้

```sql
SELECT pg_drop_replication_slot('demo_slot');
```

### 10.6 ตรวจสอบ `wal_status`

| `wal_status` | ความหมาย |
|---|---|
| `reserved` | WAL อยู่ในขอบเขต |
| `extended` | WAL เกิน `max_wal_size` แต่ยังอยู่ในขอบเขต |
| `unreserved` | WAL ถูกเก็บไว้เพราะ Slot แต่ `max_slot_wal_keep_size` ยังไม่เกิน |
| `lost` | WAL หาย — Replica ต้อง Re-sync |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: สร้าง Slot

```sql
SELECT pg_create_physical_replication_slot('pg2');
SELECT slot_name, active, wal_status, pg_size_pretty(safe_wal_size) AS safe_wal_size
FROM pg_replication_slots;
```

ผลลัพธ์:
```text
 slot_name | active | wal_status | safe_wal_size 
-----------+--------+------------+---------------
 pg2       | t      | reserved   | 10 GB
```

### ตัวอย่างที่ 2: ตรวจ WAL ที่ Slot เก็บ

```sql
SELECT slot_name,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_wal
FROM pg_replication_slots;
```

ผลลัพธ์:
```text
 slot_name | retained_wal 
-----------+--------------
 pg2       | 0 bytes
```

### ตัวอย่างที่ 3: ตั้ง `max_slot_wal_keep_size`

```sql
ALTER SYSTEM SET max_slot_wal_keep_size = '10GB';
SELECT pg_reload_conf();
```

ผลลัพธ์:
```text
ALTER SYSTEM
 pg_reload_conf 
----------------
 t
```

### ตัวอย่างที่ 4: ตรวจ Slot ที่ Inactive

```sql
SELECT slot_name, active, wal_status,
       pg_size_pretty(safe_wal_size) AS safe
FROM pg_replication_slots
WHERE NOT active;
```

### ตัวอย่างที่ 5: ลบ Slot

```sql
SELECT pg_drop_replication_slot('demo_slot');
```

## 12. สรุปย่อ จำง่าย
- **Slot = ตัวเก็บ WAL สำหรับ Replica**  
- **Physical Slot = Streaming Replication**  
- **Logical Slot = Logical Replication**  
- **`max_slot_wal_keep_size` ต้องตั้ง**  
- **Slot ค้าง = WAL บวม**  
- **ตรวจด้วย `pg_replication_slots`**

ประโยคจำ: **"Slot ที่ดีคือ Slot ที่ Active และไม่ทำให้ WAL บวม"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — Replication Slots: https://www.postgresql.org/docs/17/warm-standby.html#STREAMING-REPLICATION-SLOTS
- GridCare Workshop Day 4: Lab 1.1

---

# บทที่ 73 Patroni และ etcd

## 1. เรื่อง
Patroni และ etcd สำหรับ High Availability ของ PostgreSQL

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจสถาปัตยกรรม Patroni + etcd  
2. เพื่อให้ติดตั้ง etcd 3 โหนด  
3. เพื่อให้ตั้งค่า Patroni  
4. เพื่อให้ใช้ `patronictl`

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตั้ง etcd 3 โหนด  
- ตั้ง Patroni 2 โหนด  
- ใช้ `patronictl list`  
- ใช้ `patronictl switchover` และ `failover`

## 4. เนื้อหาโดยย่อ
**Patroni** = HA Manager ที่:
- ตรวจสอบ Primary ด้วย etcd Lock  
- Promote/Demote Replica  
- ใช้ REST API (`/primary`, `/replica`)  
- ใช้ `pg_rewind` เมื่อ Replica เดิมกลับมา

**etcd** = Distributed Key-Value Store สำหรับ Lock  
- ต้องมี Quorum (3 โหนด)  
- Patroni ใช้ etcd ในการเลือก Leader

## 5. ประโยชน์ที่ได้รับ
- HA อัตโนมัติ  
- Failover เร็ว  
- Switchover ตาม Plan  
- ไม่มี Split-Brain

## 6. ข้อควรระวัง
- **etcd ต้องมี 3 โหนด**  
- **`patronictl` ต้องใช้ sudo หรือ alias**  
- **`start.conf` ต้องเป็น `manual`**  
- **ห้ามใช้ `ALTER SYSTEM`** (ใช้ `patronictl edit-config`)  
- **`rewind_user` ต้องมีสิทธิ์ 4 ฟังก์ชัน**

## 7. ข้อดี
- HA อัตโนมัติ  
- Failover เร็ว  
- Switchover ตาม Plan  
- ไม่มี Split-Brain

## 8. ข้อเสีย
- ต้องมี etcd  
- ต้องตั้งค่า  
- Debug ยากกว่า Single Node

## 9. ข้อห้าม
- ห้ามใช้ etcd 1 โหนดบน Production  
- ห้ามใช้ `ALTER SYSTEM` กับ Patroni  
- ห้ามใช้ `pg_ctl` ตรง ๆ  
- ห้าม `start.conf = auto`  
- ห้าม lืมตั้ง `rewind_user`

## 10. รายละเอียด

### 10.1 ติดตั้ง etcd

```bash
# บน pg1, pg2, infra
sudo apt install -y etcd-server etcd-client
sudo systemctl stop etcd
sudo rm -rf /var/lib/etcd/default
```

### 10.2 ตั้ง etcd

```bash
ME=$(hostname | grep -oE '(pg1|pg2|infra)$')
ME_IP=$(getent hosts "$ME" | awk '{print $1}')
PG1_IP=$(getent hosts pg1 | awk '{print $1}')
PG2_IP=$(getent hosts pg2 | awk '{print $1}')
INFRA_IP=$(getent hosts infra | awk '{print $1}')

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

### 10.3 ตรวจสอบ etcd

```bash
E="pg1:2379,pg2:2379,infra:2379"
etcdctl --endpoints=$E endpoint health
etcdctl --endpoints=$E member list -w table
```

ผลลัพธ์:
```text
http://pg1:2379 is healthy
http://pg2:2379 is healthy
http://infra:2379 is healthy

+----------------+---------+-------+--------------------------+
| 8e9e05c52164694d | started | pg1   | http://10.104.0.11:2380 |
| 91bc3c398fb3c146 | started | pg2   | http://10.104.0.12:2380 |
| fd422379fda50e48 | started | infra | http://10.104.0.13:2380 |
+----------------+---------+-------+--------------------------+
```

### 10.4 ติดตั้ง Patroni

```bash
sudo apt install -y patroni
```

### 10.5 `patroni.yml`

**`/etc/patroni/17-main.yml`:**

```yaml
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
        archive_mode: "on"
        archive_command: "pgbackrest --stanza=gridcare archive-push %p"

postgresql:
  listen: 0.0.0.0:5432
  connect_address: ${ME_IP}:5432
  data_dir: /var/lib/postgresql/17/main
  config_dir: /etc/postgresql/17/main
  bin_dir: /usr/lib/postgresql/17/bin
  authentication:
    superuser:
      username: postgres
    replication:
      username: replicator
      password: Lab-Repl-2569
    rewind:
      username: rewind_user
      password: Lab-Rewind-2569

tags:
  nofailover: false
  noloadbalance: false
  clonefrom: false
  nosync: false
```

### 10.6 สร้าง Role rewind_user

```sql
CREATE ROLE rewind_user WITH LOGIN PASSWORD 'Lab-Rewind-2569';
GRANT EXECUTE ON FUNCTION pg_catalog.pg_ls_dir(text, boolean, boolean) TO rewind_user;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_stat_file(text, boolean) TO rewind_user;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_read_binary_file(text) TO rewind_user;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_read_binary_file(text, bigint, bigint, boolean) TO rewind_user;
```

### 10.7 สตาร์ต Patroni

```bash
sudo systemctl stop postgresql@17-main
echo manual | sudo tee /etc/postgresql/17/main/start.conf
sudo -u postgres patroni --validate-config /etc/patroni/17-main.yml
sudo systemctl enable --now patroni@17-main
sleep 15
patronictl list
```

ผลลัพธ์:
```text
+ Cluster: gridcare (7700687945522716648) ---+-------------+-----+------------+
| Member | Host      | Role   | State   | TL |
+--------+-----------+--------+---------+----+
| pg1    | 10.104... | Leader | running |  3 |
+--------+-----------+--------+---------+----+
```

### 10.8 `patronictl` Commands

| คำสั่ง | ใช้ |
|---|---|
| `patronictl list` | ดู Cluster |
| `patronictl show-config` | ดู Config |
| `patronictl edit-config` | แก้ Config |
| `patronictl switchover` | Switchover ตาม Plan |
| `patronictl failover` | Failover Emergency |
| `patronictl restart` | Restart Member |
| `patronictl reinit` | Reinit Member |
| `patronictl pause` | หยุด Auto Failover |
| `patronictl resume` | เปิด Auto Failover |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: ตั้ง etcd 3 โหนด

```bash
# บนทั้ง 3 เครื่อง
sudo apt install -y etcd-server etcd-client
# ตั้ง /etc/default/etcd ตามด้านบน
sudo systemctl start etcd
```

### ตัวอย่างที่ 2: ตั้ง Patroni

```bash
sudo systemctl enable --now patroni@17-main
sleep 15
patronictl list
```

### ตัวอย่างที่ 3: ตรวจสอบ `show-config`

```bash
patronictl show-config
```

ผลลัพธ์:
```text
loop_wait: 10
maximum_lag_on_failover: 1048576
postgresql:
  parameters:
    archive_command: pgbackrest --stanza=gridcare archive-push %p
    archive_mode: 'on'
    hot_standby: 'on'
    max_slot_wal_keep_size: 10GB
    wal_level: replica
    wal_log_hints: 'on'
  use_pg_rewind: true
  use_slots: true
retry_timeout: 10
ttl: 30
```

### ตัวอย่างที่ 4: สร้าง Replica

```bash
# บน pg2
sudo systemctl enable --now patroni@17-main
journalctl -u patroni@17-main -f
# รอ: "no action. I am (pg2), a secondary, and following a leader (pg1)"
```

### ตัวอย่างที่ 5: ตรวจสอบ `patronictl list`

```bash
patronictl list
```

ผลลัพธ์:
```text
+ Cluster: gridcare ---+-------------+-----+------------+
| Member | Host      | Role    | State     | TL |
+--------+-----------+---------+-----------+----+
| pg1    | 10.104... | Leader  | running   |  3 |
| pg2    | 10.104... | Replica | streaming |  3 |
+--------+-----------+---------+-----------+----+
```

## 12. สรุปย่อ จำง่าย
- **Patroni = HA Manager**  
- **etcd = Distributed Lock**  
- **etcd ต้อง 3 โหนด**  
- **`patronictl` ใช้จัดการ**  
- **`start.conf = manual`**  
- **`rewind_user` ต้องมี 4 ฟังก์ชัน**  
- **ห้าม `ALTER SYSTEM` กับ Patroni**

ประโยคจำ: **"Patroni + etcd ที่ดีคือ Cluster ที่มี 1 Leader และทุกคนเห็นตรงกัน"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Patroni Documentation: https://patroni.readthedocs.io/
- etcd Documentation: https://etcd.io/docs/
- GridCare Workshop Day 4: Lab 2.1, Lab 2.2

---

# บทที่ 74 HAProxy

## 1. เรื่อง
HAProxy สำหรับ Load Balancing และ Health Check ของ PostgreSQL Cluster

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจบทบาทของ HAProxy  
2. เพื่อให้ตั้ง HAProxy สำหรับ Primary/Replica  
3. เพื่อให้ใช้ Patroni REST API เป็น Health Check  
4. เพื่อให้ตรวจสอบ Stats

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- เขียน `haproxy.cfg` สำหรับ PostgreSQL  
- ใช้ `/primary` และ `/replica` Health Check  
- ตรวจ Stats ที่ Port 7000  
- ใช้ PgBouncer ผ่าน HAProxy

## 4. เนื้อหาโดยย่อ
HAProxy:
- **Port 5000** → Primary (RW)  
- **Port 5001** → Replica (RO)  
- **Port 7000** → Stats  
- Health Check ผ่าน Patroni REST API (`/primary`, `/replica`)

## 5. ประโยชน์ที่ได้รับ
- Load Balancing  
- Health Check  
- สลับ Primary อัตโนมัติ  
- Stats ชัดเจน

## 6. ข้อควรระวัง
- **Health Check ต้องใช้ Patroni REST API**  
- **`on-marked-down shutdown-sessions`** ตัด Session ที่ค้าง  
- **`maxconn` ต้องเหมาะกับ PgBouncer**  
- **Port 5000 ต้องเป็น Primary เท่านั้น**

## 7. ข้อดี
- Load Balancing  
- Health Check  
- สลับ Primary อัตโนมัติ  
- Stats

## 8. ข้อเสีย
- ต้องตั้งค่า  
- ต้องดูแล

## 9. ข้อห้าม
- ห้าม Health Check ที่ไม่ใช้ Patroni REST  
- ห้าม `balance` ระหว่าง Primary กับ Replica  
- ห้ามใช้ Port เดียวกันสำหรับ RW/RO  
- ห้าม `maxconn` ที่สูงเกิน

## 10. รายละเอียด

### 10.1 `haproxy.cfg`

```cfg
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
```

### 10.2 ตรวจสอบ

```bash
sudo haproxy -c -f /etc/haproxy/haproxy.cfg && sudo systemctl restart haproxy
```

ผลลัพธ์:
```text
Configuration file is valid
```

### 10.3 ตรวจ Stats

```bash
curl -s "http://127.0.0.1:7000/;csv" | awk -F, '$1=="primary" || $1=="replicas" {print $1, $2, $18}'
```

ผลลัพธ์:
```text
primary pg1 UP
primary pg2 DOWN
replicas pg1 DOWN
replicas pg2 UP
```

### 10.4 ชี้ PgBouncer ไปที่ HAProxy

```bash
sudo sed -i 's/^gridcare = .*/gridcare = host=127.0.0.1 port=5000 dbname=gridcare/' /etc/pgbouncer/pgbouncer.ini
sudo systemctl restart pgbouncer
```

### 10.5 ทดสอบ

```bash
psql "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" -Atc "SELECT 'via pgbouncer: ' || inet_server_addr()"
psql "host=127.0.0.1 port=5001 dbname=gridcare user=billing_app" -Atc "SELECT 'read port: ' || inet_server_addr() || ' recovery=' || pg_is_in_recovery()"
```

ผลลัพธ์:
```text
via pgbouncer: 10.104.0.11
read port: 10.104.0.12 recovery=true
```

### 10.6 ตาราง Port

| Port | ใช้ |
|---|---|
| 5000 | Primary (RW) |
| 5001 | Replica (RO) |
| 7000 | Stats |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Config พื้นฐาน

```cfg
listen primary
    bind *:5000
    option httpchk GET /primary
    http-check expect status 200
    server pg1 10.104.0.11:5432 check port 8008
    server pg2 10.104.0.12:5432 check port 8008
```

### ตัวอย่างที่ 2: ตรวจสอบ Stats

```bash
curl -s "http://127.0.0.1:7000/;csv" | awk -F, '$1=="primary" || $1=="replicas" {print $1, $2, $18}'
```

ผลลัพธ์:
```text
primary pg1 UP
primary pg2 DOWN
replicas pg1 DOWN
replicas pg2 UP
```

### ตัวอย่างที่ 3: ตรวจสอบว่า PgBouncer ไปที่ Primary

```bash
psql "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" -Atc "SELECT inet_server_addr()"
```

ผลลัพธ์:
```text
10.104.0.11
```

### ตัวอย่างที่ 4: Switchover แล้วตรวจสอบ

```bash
# บน pg1
patronictl switchover gridcare --leader pg1 --candidate pg2 --force
sleep 10
patronictl list
```

ผลลัพธ์:
```text
| pg1 | 10.104... | Replica | streaming | 4 |
| pg2 | 10.104... | Leader  | running   | 4 |
```

```bash
# บน infra
psql "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" -Atc "SELECT inet_server_addr()"
```

ผลลัพธ์:
```text
10.104.0.12
```

> ✅ IP เปลี่ยนจาก pg1 → pg2 อัตโนมัติ

## 12. สรุปย่อ จำง่าย
- **HAProxy = Load Balancer + Health Check**  
- **Port 5000 = Primary, Port 5001 = Replica**  
- **Health Check ผ่าน Patroni REST (`/primary`, `/replica`)**  
- **Port 7000 = Stats**  
- **`on-marked-down shutdown-sessions`** ตัด Session ค้าง  
- **PgBouncer → HAProxy :5000**

ประโยคจำ: **"HAProxy ที่ดีคือ HAProxy ที่รู้ว่าใครคือ Primary จริง ๆ"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- HAProxy Documentation: https://docs.haproxy.org/
- Patroni — REST API: https://patroni.readthedocs.io/en/latest/rest_api.html
- GridCare Workshop Day 4: Lab 3.1

---

# บทที่ 75 PgBouncer

## 1. เรื่อง
PgBouncer สำหรับ Connection Pooling ของ PostgreSQL

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Pool Mode  
2. เพื่อให้ตั้ง PgBouncer  
3. เพื่อให้ใช้ Auth Query  
4. เพื่อให้วัดผลด้วย pgbench

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตั้ง `pool_mode = transaction`  
- ใช้ `auth_query`  
- ตั้ง `max_db_connections`  
- วัดผล TPS ด้วย pgbench

## 4. เนื้อหาโดยย่อ
**PgBouncer** = Connection Pooler ที่:
- ลด Connection ที่ไปถึง PostgreSQL  
- ใช้ Pool Mode: Session, Transaction, Statement  
- ใช้ Auth Query  
- ใช้ Admin Console (`SHOW POOLS`)

## 5. ประโยชน์ที่ได้รับ
- ลด Connection  
- เพิ่ม TPS  
- ลด Memory  
- ทำให้ระบบรองรับ Client มากขึ้น

## 6. ข้อควรระวัง
- **`pool_mode = transaction` ไม่รองรับ Prepared Statement บางแบบ**  
- **`auth_file` ต้องเป็น Plain Password** (ถ้าใช้ SCRAM secret จะไม่ได้)  
- **`server_tls_sslmode = require`** ใน Production  
- **`max_db_connections` ต้องเหมาะกับ PostgreSQL**

## 7. ข้อดี
- ลด Connection  
- เพิ่ม TPS  
- ลด Memory  
- รองรับ Client มากขึ้น

## 8. ข้อเสีย
- ไม่รองรับ Prepared Statement บางแบบ  
- ต้องตั้ง Auth Query  
- Debug ยากกว่า Direct

## 9. ข้อห้าม
- ห้าม `pool_mode = session` ถ้าต้องการ Performance  
- ห้ามใช้ SCRAM secret ใน `userlist.txt`  
- ห้าม `max_db_connections` สูงเกิน PostgreSQL  
- ห้ามใช้ PgBouncer เป็นที่เก็บ Password

## 10. รายละเอียด

### 10.1 สร้าง Auth Function

```sql
CREATE SCHEMA pgbouncer AUTHORIZATION postgres;
REVOKE ALL ON SCHEMA pgbouncer FROM PUBLIC;
GRANT USAGE ON SCHEMA pgbouncer TO pgbouncer_auth;

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

### 10.2 `pgbouncer.ini`

```ini
[databases]
gridcare = host=127.0.0.1 port=5000 dbname=gridcare

[pgbouncer]
listen_addr = *
listen_port = 6432
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

### 10.3 `userlist.txt`

```text
"pgbouncer_auth" "Lab-PgbAuth-2569"
"pgbouncer_admin" "Lab-PgbAdmin-2569"
```

> ⚠️ ต้องเป็น Plain Password ไม่ใช่ SCRAM Secret

### 10.4 Restart

```bash
sudo systemctl restart pgbouncer
sudo tail -n 5 /var/log/postgresql/pgbouncer.log
```

ผลลัพธ์:
```text
LOG listening on 0.0.0.0:6432
LOG process up: PgBouncer 1.26.1, libevent 2.1.12-stable (epoll), adns: evdns2, tls: OpenSSL 3.0.13
```

### 10.5 วัดผล

**ต่อตรง:**
```bash
PGHOST=pg1 PGPORT=5432 PGUSER=billing_app PGSSLMODE=require \
  pgbench -n -C -c 50 -j 2 -T 60 -f lookup_customer.sql -f report_outage.sql gridcare
```

ผลลัพธ์:
```text
number of transactions actually processed: 3421
latency average = 878.234 ms
tps = 57.012345
```

**ผ่าน PgBouncer:**
```bash
PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app \
  pgbench -n -C -c 50 -j 2 -T 60 -f lookup_customer.sql -f report_outage.sql gridcare
```

ผลลัพธ์:
```text
number of transactions actually processed: 5589
latency average = 536.892 ms
tps = 93.123456
```

### 10.6 `SHOW POOLS`

```sql
SHOW POOLS;
```

ผลลัพธ์:
```text
 database  |   user      | cl_active | cl_waiting | sv_active | sv_idle | pool_mode 
-----------+-------------+-----------+------------+-----------+---------+-----------
 gridcare  | billing_app |        50 |          0 |        20 |       0 | transaction
```

### 10.7 ตาราง Pool Mode

| Pool Mode | ใช้ |
|---|---|
| Session | Session เดียวตลอด |
| Transaction | Pool ต่อ Transaction |
| Statement | Pool ต่อ Statement |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Auth Function

```sql
CREATE SCHEMA pgbouncer AUTHORIZATION postgres;
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
```

### ตัวอย่างที่ 2: ตั้ง PgBouncer

```ini
[databases]
gridcare = host=127.0.0.1 port=5000 dbname=gridcare

[pgbouncer]
pool_mode = transaction
default_pool_size = 20
max_db_connections = 40
auth_type = scram-sha-256
auth_query = SELECT uname, phash FROM pgbouncer.user_lookup($1)
```

### ตัวอย่างที่ 3: วัด TPS

```bash
PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app \
  pgbench -n -C -c 50 -j 2 -T 60 -f lookup_customer.sql -f report_outage.sql gridcare
```

ผลลัพธ์:
```text
tps = 93.123456
```

### ตัวอย่างที่ 4: ตรวจ `SHOW POOLS`

```sql
SHOW POOLS;
```

ผลลัพธ์:
```text
 database  |   user      | cl_active | sv_active | sv_idle | pool_mode 
-----------+-------------+-----------+-----------+---------+-----------
 gridcare  | billing_app |        50 |        20 |       0 | transaction
```

### ตัวอย่างที่ 5: เปรียบเทียบ Before/After

| วิธี | tps | latency |
|---|---|---|
| Direct pg1 | 57 | 878 ms |
| **PgBouncer** | **93** | **536 ms** |

> ✅ **+63% tps, -39% latency**

## 12. สรุปย่อ จำง่าย
- **PgBouncer = Connection Pooler**  
- **`pool_mode = transaction`** สำหรับ Performance  
- **`auth_query` ดีกว่า `auth_file`**  
- **`max_db_connections` ต้องเหมาะ**  
- **`server_tls_sslmode = require`**  
- **วัดผลด้วย pgbench**

ประโยคจำ: **"PgBouncer ที่ดีคือ PgBouncer ที่ลด Connection แต่เพิ่ม TPS"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PgBouncer Documentation: https://www.pgbouncer.org/
- GridCare Workshop Day 1: ขั้นที่ 3

---

# บทที่ 76 Switchover

## 1. เรื่อง
การทำ Switchover ใน Patroni Cluster ตามแผน (Planned Switchover)

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Switchover vs Failover  
2. เพื่อให้ทำ Switchover ตาม Plan  
3. เพื่อให้ตรวจสอบผล  
4. เพื่อให้ตรวจสอบว่า Application ยังทำงานได้

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- รัน `patronictl switchover`  
- ตรวจสอบ `patronictl list`  
- ตรวจสอบว่า HAProxy สลับ  
- ตรวจสอบว่า PgBouncer ยังทำงาน

## 4. เนื้อหาโดยย่อ
**Switchover** = สลับ Primary ตามแผน → RPO = 0, Downtime ~3 วินาที  
**Failover** = สลับ Primary เมื่อ Primary ล่ม → RPO > 0, Downtime ตาม Detection

## 5. ประโยชน์ที่ได้รับ
- สลับ Primary ได้ตาม Plan  
- RPO = 0  
- Downtime ต่ำ  
- ใช้ใน Maintenance

## 6. ข้อควรระวัง
- **ต้องตรวจว่า Candidate พร้อม**  
- **ต้องตรวจว่า HAProxy สลับ**  
- **ต้องตรวจว่า PgBouncer ยังทำงาน**  
- **ต้องตรวจว่า Application ยังทำงาน**  
- **ต้อง Full Backup หลัง Switchover**

## 7. ข้อดี
- RPO = 0  
- Downtime ต่ำ  
- ตาม Plan

## 8. ข้อเสีย
- ต้อง Plan  
- ต้องตรวจ Candidate

## 9. ข้อห้าม
- ห้าม Switchover ไปที่ Replica ที่ Lag สูง  
- ห้าม Switchover โดยไม่ตรวจ Candidate  
- ห้าม Switchover ในช่วง Peak Hours  
- ห้ามลืม Full Backup หลัง Switchover

## 10. รายละเอียด

### 10.1 ตรวจสอบสถานะก่อน

```bash
patronictl list
```

ผลลัพธ์:
```text
+ Cluster: gridcare +-------------+---------+----+------------+
| pg1 | 10.104... | Leader  | running   | 3 |
| pg2 | 10.104... | Replica | streaming | 3 |
+--------+-----------+---------+-----------+----+
```

### 10.2 Switchover

```bash
patronictl switchover gridcare --leader pg1 --candidate pg2 --force
sleep 10
patronictl list
```

ผลลัพธ์:
```text
+ Cluster: gridcare +-------------+---------+----+------------+
| pg1 | 10.104... | Replica | streaming | 4 |
| pg2 | 10.104... | Leader  | running   | 4 |
+--------+-----------+---------+-----------+----+
```

### 10.3 ตรวจสอบ HAProxy

```bash
curl -s "http://127.0.0.1:7000/;csv" | awk -F, '$1=="primary" || $1=="replicas" {print $1, $2, $18}'
```

ผลลัพธ์:
```text
primary pg1 DOWN
primary pg2 UP
replicas pg1 UP
replicas pg2 DOWN
```

### 10.4 ตรวจสอบ PgBouncer

```bash
psql "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" -Atc "SELECT inet_server_addr()"
```

ผลลัพธ์:
```text
10.104.0.12
```

### 10.5 Switchover กลับ

```bash
patronictl switchover gridcare --leader pg2 --candidate pg1 --force
```

### 10.6 วัด Downtime ด้วย Probe

```bash
~/probe.sh 60 | tee ~/probe-switchover.log
echo "FAIL = $(grep -c ' FAIL ' ~/probe-switchover.log) ครั้ง"
```

ผลลัพธ์:
```text
FAIL = 0 ครั้ง
```

> ✅ Switchover ตามแผนใช้เวลา ~3 วินาที

### 10.7 Full Backup ใหม่

```bash
sudo -u postgres pgbackrest --stanza=gridcare check
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Switchover ตาม Plan

```bash
patronictl switchover gridcare --leader pg1 --candidate pg2 --force
sleep 10
patronictl list
```

ผลลัพธ์:
```text
Switchover settled in 3s
| pg1 | ... | Replica | streaming | 4 |
| pg2 | ... | Leader  | running   | 4 |
```

### ตัวอย่างที่ 2: ตรวจ HAProxy

```bash
curl -s "http://127.0.0.1:7000/;csv" | awk -F, '$1=="primary" || $1=="replicas" {print $1, $2, $18}'
```

ผลลัพธ์:
```text
primary pg2 UP
primary pg1 DOWN
replicas pg1 UP
replicas pg2 DOWN
```

### ตัวอย่างที่ 3: ตรวจ PgBouncer

```bash
psql "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" -Atc "SELECT inet_server_addr()"
```

ผลลัพธ์:
```text
10.104.0.12
```

### ตัวอย่างที่ 4: วัด Downtime

```bash
~/probe.sh 60 | tee ~/probe-switchover.log
echo "FAIL = $(grep -c ' FAIL ' ~/probe-switchover.log) ครั้ง"
```

ผลลัพธ์:
```text
FAIL = 0 ครั้ง
```

### ตัวอย่างที่ 5: Switchover กลับ

```bash
patronictl switchover gridcare --leader pg2 --candidate pg1 --force
sleep 10
patronictl list
```

## 12. สรุปย่อ จำง่าย
- **Switchover = Planned**  
- **RPO = 0**  
- **Downtime ~3 วินาที**  
- **ตรวจด้วย `patronictl list`**  
- **ตรวจ HAProxy + PgBouncer**  
- **Full Backup หลัง Switchover**

ประโยคจำ: **"Switchover ที่ดีคือ Switchover ที่ Application ไม่รู้ตัว"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Patroni — Switchover: https://patroni.readthedocs.io/en/latest/rest_api.html#switchover
- GridCare Workshop Day 4: Lab 3.1

---

# บทที่ 77 Failover

## 1. เรื่อง
การทำ Failover ใน Patroni Cluster เมื่อ Primary ล่ม

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Failover  
2. เพื่อให้วัด RTO/RPO  
3. เพื่อให้ตรวจสอบ Alert  
4. เพื่อให้ตรวจสอบผล

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- วัด RTO/RPO  
- ตรวจสอบ `patronictl list`  
- ตรวจสอบ Alert  
- ตรวจสอบว่า Application ยังทำงาน

## 4. เนื้อหาโดยย่อ
**Failover** = สลับ Primary เมื่อ Primary ล่ม  
- Patroni ตรวจพบภายใน `loop_wait`  
- Promote Replica ภายใน `ttl`  
- RTO ~30–45 วินาที  
- RPO ขึ้นกับ Sync/Async

## 5. ประโยชน์ที่ได้รับ
- HA อัตโนมัติ  
- RTO/RPO ที่วัดได้  
- ลด Downtime  
- ผ่าน Game Day

## 6. ข้อควรระวัง
- **RPO ขึ้นกับ Sync/Async**  
- **ต้องมี Quorum (etcd)**  
- **ต้องมี `pg_rewind`**  
- **ต้องตรวจ Application**  
- **ต้อง Full Backup หลัง Failover**

## 7. ข้อดี
- HA อัตโนมัติ  
- RTO/RPO วัดได้  
- ผ่าน Game Day

## 8. ข้อเสีย
- ต้องมี etcd  
- ต้องมี `pg_rewind`  
- RPO > 0 ถ้า Async

## 9. ข้อห้าม
- ห้าม Failover โดยไม่มี Quorum  
- ห้าม Failover โดยไม่มี `pg_rewind`  
- ห้าม Failover ในช่วงที่ต้อง Sync  
- ห้ามลืม Full Backup หลัง Failover

## 10. รายละเอียด

### 10.1 เตรียม Probe

**บน pg1:**
```sql
CREATE TABLE gridcare.failover_probe (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ts timestamptz NOT NULL DEFAULT clock_timestamp(),
    served_by inet DEFAULT inet_server_addr()
);
GRANT INSERT, SELECT ON gridcare.failover_probe TO gridcare_write;
```

**บน infra:**
```bash
#!/usr/bin/env bash
# ~/probe.sh
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

### 10.2 เปิดโหลด

```bash
# หน้าต่าง 1 (infra)
cd /opt/gridcare/pgbench && PGHOST=127.0.0.1 PGPORT=6432 PGUSER=billing_app ./run_payday.sh 20 600
# หน้าต่าง 2 (infra)
~/probe.sh 180 | tee ~/probe.log
```

### 10.3 Kill Primary

```bash
# หน้าต่าง 3 (pg1)
date +%T.%N | cut -c1-12
sudo systemctl kill -s SIGKILL patroni@17-main
```

ผลลัพธ์:
```text
03:03:43.351
```

### 10.4 ตรวจสอบ

```bash
# บน pg2
patronictl list
```

ผลลัพธ์:
```text
| pg1 | 10.104... | Replica | stopped   | 5 |
| pg2 | 10.104... | Leader  | running   | 6 |
```

### 10.5 วัด RTO

```bash
KILL_AT=03:03:43.351
FIRST_OK=$(awk '/ FAIL /{f=1} f && / OK /{print $1; exit}' ~/probe.log)
python3 -c "from datetime import datetime as d; f='%H:%M:%S.%f'; print('RTO =', round((d.strptime('$FIRST_OK', f) - d.strptime('$KILL_AT', f)).total_seconds(), 1), 'วินาที')"
```

ผลลัพธ์:
```text
RTO = 31.3 วินาที
```

### 10.6 วัด RPO

```bash
psql -X -At "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" \
  -c "SELECT id FROM gridcare.failover_probe ORDER BY id" | sort > ~/db_ids.txt
grep ' OK id=' ~/probe.log | sed 's/.*id=//' | sort > ~/ok_ids.txt
comm -23 ~/ok_ids.txt ~/db_ids.txt > ~/missing_ids.txt
echo "RPO = $(wc -l < ~/missing_ids.txt)"
```

ผลลัพธ์:
```text
RPO = 0
```

### 10.7 ตรวจ Alert

```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

ผลลัพธ์:
```text
"alertname": "PostgresDown",
"state": "firing"
"alertname": "PatroniPrimaryCountNotOne",
"state": "firing"
```

### 10.8 นำ Primary เดิมกลับ

```bash
# บน pg1
sudo systemctl start patroni@17-main
journalctl -u patroni@17-main -f
# รอ: "running pg_rewind from pg2"
# รอ: "no action. I am (pg1), a secondary"
```

### 10.9 ตรวจผล

```bash
patronictl list
```

ผลลัพธ์:
```text
| pg1 | 10.104... | Replica | streaming | 6 |
| pg2 | 10.104... | Leader  | running   | 6 |
```

### 10.10 Full Backup ใหม่

```bash
sudo -u postgres pgbackrest --stanza=gridcare --type=full backup
```

### 10.11 ตาราง RTO/RPO

| ตัวชี้วัด | ค่า | หมายเหตุ |
|---|---|---|
| RTO | 31.3 วินาที | Async |
| RPO | 0 | ไม่มีข้อมูลหาย |
| Downtime | ~31 วินาที | Connection refused |

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Probe Log

```bash
~/probe.sh 180 | tee ~/probe.log
```

ผลลัพธ์:
```text
03:03:40.123 OK id=1001
03:03:41.234 OK id=1002
03:03:42.345 OK id=1003
03:03:43.456 FAIL connection to server at "127.0.0.1", port 6432 failed: Connection refused
...
03:04:14.789 OK id=1004
03:04:15.890 OK id=1005
```

### ตัวอย่างที่ 2: คำนวณ RTO

```bash
KILL_AT=03:03:43.351
FIRST_OK=$(awk '/ FAIL /{f=1} f && / OK /{print $1; exit}' ~/probe.log)
python3 -c "from datetime import datetime as d; f='%H:%M:%S.%f'; print('RTO =', round((d.strptime('$FIRST_OK', f) - d.strptime('$KILL_AT', f)).total_seconds(), 1), 'วินาที')"
```

ผลลัพธ์:
```text
RTO = 31.3 วินาที
```

### ตัวอย่างที่ 3: คำนวณ RPO

```bash
psql -X -At "host=127.0.0.1 port=6432 dbname=gridcare user=billing_app" \
  -c "SELECT id FROM gridcare.failover_probe ORDER BY id" | sort > ~/db_ids.txt
grep ' OK id=' ~/probe.log | sed 's/.*id=//' | sort > ~/ok_ids.txt
comm -23 ~/ok_ids.txt ~/db_ids.txt > ~/missing_ids.txt
echo "RPO = $(wc -l < ~/missing_ids.txt)"
```

ผลลัพธ์:
```text
RPO = 0
```

### ตัวอย่างที่ 4: ตรวจ Alert

```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

ผลลัพธ์:
```text
"alertname": "PostgresDown",
"state": "firing"
"alertname": "PatroniPrimaryCountNotOne",
"state": "firing"
```

### ตัวอย่างที่ 5: นำ Primary เดิมกลับ

```bash
sudo systemctl start patroni@17-main
journalctl -u patroni@17-main -f
```

ผลลัพธ์:
```text
INFO: running pg_rewind from pg2
INFO: pg_rewind exit code=0
INFO: no action. I am (pg1), a secondary, and following a leader (pg2)
```

## 12. สรุปย่อ จำง่าย
- **Failover = Emergency**  
- **RTO ~30–45 วินาที**  
- **RPO = 0 ถ้า Sync**  
- **RPO > 0 ถ้า Async**  
- **Patroni ใช้ `pg_rewind`**  
- **Full Backup หลัง Failover**

ประโยคจำ: **"Failover ที่ดีคือ Failover ที่วัดได้และบันทึกได้"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Patroni — Failover: https://patroni.readthedocs.io/en/latest/rest_api.html#failover
- Google SRE Book — Managing Incidents: https://sre.google/sre-book/managing-incidents/
- GridCare Workshop Day 4: Workshop Day 4 ขั้นที่ 2

---

# บทที่ 78 Split-Brain

## 1. เรื่อง
Split-Brain ใน PostgreSQL Cluster สาเหตุ ผลกระทบ และวิธีป้องกัน

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Split-Brain  
2. เพื่อให้ตรวจสอบ Split-Brain  
3. เพื่อให้ป้องกันด้วย Quorum  
4. เพื่อให้แก้ไขเมื่อเกิด

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- อธิบาย Split-Brain  
- ใช้ Quorum ป้องกัน  
- ตรวจสอบด้วย `patronictl list`  
- แก้ไขเมื่อเกิด

## 4. เนื้อหาโดยย่อ
**Split-Brain** = สถานะที่มี Primary มากกว่าหนึ่งตัว  
สาเหตุ:
- Network Partition  
- etcd ไม่มี Quorum  
- Patroni ไม่สามารถ Update Lock

ผลกระทบ:
- ข้อมูลเสียหาย  
- Conflict  
- ต้อง PITR

การป้องกัน:
- Quorum (etcd 3 โหนด)  
- `ttl` ที่เหมาะ  
- `retry_timeout`

## 5. ประโยชน์ที่ได้รับ
- ป้องกันข้อมูลเสียหาย  
- ลด Downtime  
- ผ่าน Audit

## 6. ข้อควรระวัง
- **etcd 1 โหนดเสี่ยง Split-Brain**  
- **`ttl` สั้นเกินไปทำให้ Failover ถี่**  
- **`ttl` ยาวเกินไปทำให้ Downtime นาน**  
- **Network Partition เป็นสาเหตุหลัก**  
- **ต้องมี Monitoring**

## 7. ข้อดี
- ป้องกันข้อมูลเสียหาย  
- ลด Downtime

## 8. ข้อเสีย
- ต้องมี etcd 3 โหนด  
- ต้องตั้งค่าให้เหมาะ

## 9. ข้อห้าม
- ห้าม etcd 1 โหนดบน Production  
- ห้าม Patroni ที่ไม่มี etcd  
- ห้าม Network ที่ไม่เสถียร  
- ห้าม `ttl` ที่ไม่เหมาะ

## 10. รายละเอียด

### 10.1 สาเหตุ

```text
Network Partition
   │
   ▼
pg1 ──X── pg2
   │
   ▼
pg1 ยังเป็น Leader (Local)
pg2 Promote เป็น Leader (Quorum)
   │
   ▼
Split-Brain: 2 Primary
```

### 10.2 ตรวจสอบ

```sql
-- บนทุก Instance
SELECT pg_is_in_recovery(), inet_server_addr();
```

```bash
# บน Patroni
patronictl list
```

ผลลัพธ์ (Split-Brain):
```text
| pg1 | 10.104... | Leader | running | 5 |
| pg2 | 10.104... | Leader | running | 5 |
```

> ⚠️ 2 Leader = Split-Brain

### 10.3 การป้องกัน

**etcd 3 โหนด:**
```bash
etcdctl --endpoints=$E member list -w table
```

ผลลัพธ์:
```text
| pg1   | started |
| pg2   | started |
| infra | started |
```

**Patroni Config:**
```yaml
bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
```

- `ttl` = 30s → Leader Lock หมดอายุใน 30s  
- `loop_wait` = 10s → ตรวจทุก 10s  
- `retry_timeout` = 10s → รอ 10s ก่อน Retry

### 10.4 Simulate Split-Brain

```bash
# บน pg1
PG2_IP=$(getent hosts pg2 | awk '{print $1}')
INFRA_IP=$(getent hosts infra | awk '{print $1}')
sudo iptables -I INPUT 1 -s "$PG2_IP" -j DROP
sudo iptables -I INPUT 1 -s "$INFRA_IP" -j DROP
sudo iptables -I OUTPUT 1 -d "$PG2_IP" -j DROP
sudo iptables -I OUTPUT 1 -d "$INFRA_IP" -j DROP
```

ผลลัพธ์ (หลัง 30-40 วินาที):
```text
# บน pg1
WARNING: failed to update leader lock
INFO: demoting self because DCS is not accessible and I was a leader
INFO: no action. I am (pg1), a secondary, and following a leader (pg2)
```

> ✅ Patroni Demote ตัวเอง → ป้องกัน Split-Brain

### 10.5 ตรวจสอบ

```bash
# บน pg1
sudo -u postgres psql -XAtc "SELECT 'pg1 in_recovery=' || pg_is_in_recovery()"
```

ผลลัพธ์:
```text
pg1 in_recovery=true
```

```bash
# บน pg2
patronictl list
```

ผลลัพธ์:
```text
| pg1 | 10.104... | Replica | stopped   | 4 |
| pg2 | 10.104... | Leader  | running   | 5 |
```

### 10.6 คืน Network

```bash
sudo iptables -D INPUT -s "$PG2_IP" -j DROP
sudo iptables -D INPUT -s "$INFRA_IP" -j DROP
sudo iptables -D OUTPUT -d "$PG2_IP" -j DROP
sudo iptables -D OUTPUT -d "$INFRA_IP" -j DROP
```

### 10.7 ตรวจสอบหลังคืน

```bash
patronictl list
```

ผลลัพธ์:
```text
| pg1 | 10.104... | Replica | streaming | 5 |
| pg2 | 10.104... | Leader  | running   | 5 |
```

### 10.8 แก้ไขเมื่อเกิด Split-Brain

**ขั้นตอน:**
1. หยุด Instance ที่เป็น Leader โดยไม่ควรเป็น  
2. ตรวจสอบ `pg_is_in_recovery()`  
3. ใช้ `pg_rewind` หรือ Reinit  
4. ตรวจสอบข้อมูล  
5. Full Backup

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: จำลอง Split-Brain ด้วย iptables

```bash
sudo iptables -I INPUT 1 -s "$PG2_IP" -j DROP
sudo iptables -I INPUT 1 -s "$INFRA_IP" -j DROP
sudo iptables -I OUTPUT 1 -d "$PG2_IP" -j DROP
sudo iptables -I OUTPUT 1 -d "$INFRA_IP" -j DROP
```

### ตัวอย่างที่ 2: ตรวจสอบ Patroni

```bash
journalctl -u patroni@17-main -n 10 --no-pager
```

ผลลัพธ์:
```text
WARNING: failed to update leader lock
INFO: demoting self because DCS is not accessible and I was a leader
INFO: no action. I am (pg1), a secondary, and following a leader (pg2)
```

### ตัวอย่างที่ 3: ตรวจสอบ `pg_is_in_recovery`

```bash
sudo -u postgres psql -XAtc "SELECT 'pg1 in_recovery=' || pg_is_in_recovery()"
```

ผลลัพธ์:
```text
pg1 in_recovery=true
```

### ตัวอย่างที่ 4: ตรวจ Alert

```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

ผลลัพธ์:
```text
"alertname": "PatroniPrimaryCountNotOne",
"state": "firing"
```

### ตัวอย่างที่ 5: คืน Network

```bash
sudo iptables -D INPUT -s "$PG2_IP" -j DROP
sudo iptables -D INPUT -s "$INFRA_IP" -j DROP
sudo iptables -D OUTPUT -d "$PG2_IP" -j DROP
sudo iptables -D OUTPUT -d "$INFRA_IP" -j DROP
sleep 30
patronictl list
```

## 12. สรุปย่อ จำง่าย
- **Split-Brain = 2 Primary**  
- **สาเหตุ: Network Partition, etcd ไม่มี Quorum**  
- **ป้องกัน: etcd 3 โหนด + Quorum**  
- **`ttl` 30s, `loop_wait` 10s**  
- **ตรวจด้วย `patronictl list`**  
- **`pg_is_in_recovery` = true คือปลอดภัย**

ประโยคจำ: **"Split-Brain คือศัตรูที่ต้องป้องกันด้วย Quorum ไม่ใช่ด้วยความหวัง"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Patroni — Quorum: https://patroni.readthedocs.io/en/latest/
- etcd — Quorum: https://etcd.io/docs/
- GridCare Workshop Day 4: Lab 3.2

---

# บทที่ 79 pg_rewind

## 1. เรื่อง
`pg_rewind` สำหรับ Sync Replica เดิมกลับมาโดยไม่ต้อง Rebase

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ `pg_rewind`  
2. เพื่อให้ตั้ง `rewind_user`  
3. เพื่อให้ `pg_rewind` ทำงาน  
4. เพื่อให้ตรวจสอบผล

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตั้ง `rewind_user` ให้มีสิทธิ์ 4 ฟังก์ชัน  
- ใช้ `pg_rewind`  
- ตรวจสอบ `pg_rewind exit code=0`  
- ตรวจสอบว่า Replica กลับมา Streaming

## 4. เนื้อหาโดยย่อ
`pg_rewind` = เครื่องมือ Sync Replica เดิมกลับมาโดย:
- อ่าน WAL จาก Primary ใหม่  
- เปรียบเทียบ Timeline  
- คัดลอกเฉพาะ Block ที่เปลี่ยน

ข้อดี: เร็วกว่า `pg_basebackup`  
ข้อจำกัด: ต้องมี `wal_log_hints = on` หรือ `data_checksums = on`

## 5. ประโยชน์ที่ได้รับ
- เร็วกว่า Rebase  
- ลด Downtime  
- ลด Network  
- ทำให้ Replica กลับมาเร็ว

## 6. ข้อควรระวัง
- **ต้องมี `wal_log_hints = on` หรือ `data_checksums = on`**  
- **`rewind_user` ต้องมีสิทธิ์ 4 ฟังก์ชัน**  
- **ต้องหยุด Replica ก่อน `pg_rewind`**  
- **`pg_rewind` ไม่ใช่ Backup**  
- **ต้องตรวจ `pg_rewind exit code=0`**

## 7. ข้อดี
- เร็วกว่า Rebase  
- ลด Network  
- ลด Downtime

## 8. ข้อเสีย
- ต้องมี `wal_log_hints`  
- ต้องตั้ง `rewind_user`  
- ไม่ใช่ Backup

## 9. ข้อห้าม
- ห้าม `pg_rewind` บน Primary  
- ห้าม `pg_rewind` โดยไม่มี `wal_log_hints`  
- ห้าม `pg_rewind` โดยไม่หยุด Replica  
- ห้าม `pg_rewind` แทน Backup

## 10. รายละเอียด

### 10.1 สร้าง `rewind_user`

```sql
CREATE ROLE rewind_user WITH LOGIN PASSWORD 'Lab-Rewind-2569';
GRANT EXECUTE ON FUNCTION pg_catalog.pg_ls_dir(text, boolean, boolean) TO rewind_user;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_stat_file(text, boolean) TO rewind_user;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_read_binary_file(text) TO rewind_user;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_read_binary_file(text, bigint, bigint, boolean) TO rewind_user;
```

### 10.2 ตั้ง `wal_log_hints`

```ini
wal_log_hints = on
```

หรือใช้ `data_checksums = on` (เทียบเท่า)

### 10.3 `pg_rewind` ด้วยตนเอง

```bash
sudo systemctl stop postgresql@17-main
sudo -u postgres /usr/lib/postgresql/17/bin/pg_rewind \
  --target-pgdata=/var/lib/postgresql/17/main \
  --source-server="host=pg2 port=5432 user=postgres dbname=postgres"
```

ผลลัพธ์:
```text
pg_rewind: servers diverged at WAL location 0/3000028 on timeline 4
pg_rewind: rewinding from last common checkpoint at 0/2000028 on timeline 4
pg_rewind: Done!
pg_rewind: exit code=0
```

### 10.4 Patroni `pg_rewind`

Patroni ใช้ `pg_rewind` อัตโนมัติ:

```text
INFO: running pg_rewind from pg2
INFO: pg_rewind exit code=0
INFO: no action. I am (pg1), a secondary, and following a leader (pg2)
```

### 10.5 ตรวจสอบ

```bash
patronictl list
```

ผลลัพธ์:
```text
| pg1 | 10.104... | Replica | streaming | 6 |
| pg2 | 10.104... | Leader  | running   | 6 |
```

### 10.6 ตรวจสอบ `wal_log_hints`

```sql
SHOW wal_log_hints;
SHOW data_checksums;
```

ผลลัพธ์:
```text
 wal_log_hints 
---------------
 on

 data_checksums 
----------------
 on
```

> ✅ ต้องมีอย่างน้อยหนึ่งตัว

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: สร้าง `rewind_user`

```sql
CREATE ROLE rewind_user WITH LOGIN PASSWORD 'Lab-Rewind-2569';
GRANT EXECUTE ON FUNCTION pg_catalog.pg_ls_dir(text, boolean, boolean) TO rewind_user;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_stat_file(text, boolean) TO rewind_user;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_read_binary_file(text) TO rewind_user;
GRANT EXECUTE ON FUNCTION pg_catalog.pg_read_binary_file(text, bigint, bigint, boolean) TO rewind_user;
```

### ตัวอย่างที่ 2: `pg_rewind` ด้วยตนเอง

```bash
sudo systemctl stop postgresql@17-main
sudo -u postgres /usr/lib/postgresql/17/bin/pg_rewind \
  --target-pgdata=/var/lib/postgresql/17/main \
  --source-server="host=pg2 port=5432 user=postgres dbname=postgres"
```

ผลลัพธ์:
```text
pg_rewind: Done!
pg_rewind: exit code=0
```

### ตัวอย่างที่ 3: Patroni `pg_rewind`

```bash
sudo systemctl start patroni@17-main
journalctl -u patroni@17-main -f
```

ผลลัพธ์:
```text
INFO: running pg_rewind from pg2
INFO: pg_rewind exit code=0
INFO: no action. I am (pg1), a secondary, and following a leader (pg2)
```

### ตัวอย่างที่ 4: ตรวจสอบ `patronictl list`

```bash
patronictl list
```

ผลลัพธ์:
```text
| pg1 | 10.104... | Replica | streaming | 6 |
| pg2 | 10.104... | Leader  | running   | 6 |
```

### ตัวอย่างที่ 5: ตรวจสอบ `wal_log_hints`

```sql
SHOW wal_log_hints;
```

ผลลัพธ์:
```text
 wal_log_hints 
---------------
 on
```

## 12. สรุปย่อ จำง่าย
- **`pg_rewind` = Sync Replica เดิมกลับมา**  
- **ต้องมี `wal_log_hints = on` หรือ `data_checksums = on`**  
- **`rewind_user` ต้องมีสิทธิ์ 4 ฟังก์ชัน**  
- **Patroni ใช้ `pg_rewind` อัตโนมัติ**  
- **ตรวจ `pg_rewind exit code=0`**  
- **ไม่ใช่ Backup**

ประโยคจำ: **"`pg_rewind` ทำให้ Replica กลับมา โดยไม่ต้อง Rebase"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- PostgreSQL Documentation — pg_rewind: https://www.postgresql.org/docs/17/app-pgrewind.html
- Patroni — pg_rewind: https://patroni.readthedocs.io/en/latest/replication_modes.html
- GridCare Workshop Day 4: Workshop Day 4 ขั้นที่ 3

---

# บทที่ 80 HA Monitoring และ Alert

## 1. เรื่อง
Monitoring และ Alert สำหรับ PostgreSQL HA ด้วย Patroni, HAProxy และ PgBouncer

## 2. วัตถุประสงค์ของหัวข้อ
1. เพื่อให้เข้าใจ Metric ของ HA  
2. เพื่อให้ตั้ง Alert ที่เหมาะสม  
3. เพื่อให้ตรวจสอบ Split-Brain  
4. เพื่อให้ตรวจสอบ Replication Lag

## 3. เป้าหมายของหัวข้อ
เมื่ออ่านจบ ผู้อ่านสามารถ:
- ตั้ง Alert `PatroniPrimaryCountNotOne`  
- ตั้ง Alert `PostgresReplicationLagHigh`  
- ตั้ง Alert `PostgresReplicationSlotInactive`  
- ตรวจสอบ HAProxy Stats

## 4. เนื้อหาโดยย่อ
Metric HA ที่สำคัญ:
- `patroni_primary` — จำนวน Primary  
- `pg_stat_replication_pg_wal_lsn_diff` — Replication Lag  
- `pg_replication_slots_active` — Slot Active  
- `pg_replication_slots_pg_wal_status` — Slot Status  
- `pg_up` — PostgreSQL Up

## 5. ประโยชน์ที่ได้รับ
- ตรวจพบ Split-Brain  
- ตรวจพบ Replication Lag  
- ตรวจพบ Slot Inactive  
- ตรวจพบ HAProxy Down

## 6. ข้อควรระวัง
- **`patroni_primary` ต้องมี**  
- **`pg_stat_replication_pg_wal_lsn_diff` ต้องมี Label `application_name`**  
- **Alert `PostgresDown` ต้องมี `for: 1m`**  
- **`PatroniPrimaryCountNotOne` ต้องเป็น Critical**  
- **Replication Lag Alert ต้องมี Threshold ที่เหมาะ**

## 7. ข้อดี
- ตรวจพบ Split-Brain  
- ตรวจพบ Lag  
- ตรวจพบ HAProxy Down

## 8. ข้อเสีย
- ต้องตั้ง Metric  
- ต้องตั้ง Alert  
- ต้องมี Patroni Exporter

## 9. ข้อห้าม
- ห้าม Alert ที่ไม่มี `for:`  
- ห้าม Alert ที่ไม่ actionable  
- ห้าม Alert ที่ไม่มี Runbook  
- ห้าม Alert ที่ Cardinality สูง

## 10. รายละเอียด

### 10.1 Alert Rule

```yaml
groups:
  - name: gridcare-ha
    rules:
      - alert: PatroniPrimaryCountNotOne
        expr: sum by (scope) (patroni_primary) != 1
        for: 1m
        labels: {severity: critical, owner: dba}
        annotations:
          summary: "คลัสเตอร์ {{ $labels.scope }} มี Primary {{ $value }} ตัว"
          description: "0 = ไม่มีโหนดใดรับเขียน, 2 = เสี่ยง Split-Brain ตรวจด้วย patronictl list"
          runbook_url: "http://gridcare-infra/runbooks/C08-replication-lag-slot-failover.md"

      - alert: PostgresReplicationLagHigh
        expr: max by (instance, application_name) (pg_stat_replication_pg_wal_lsn_diff) > 100 * 1024 * 1024
        for: 5m
        labels: {severity: warning, owner: dba}
        annotations:
          summary: "Replication Lag > 100 MB"
          description: "ตรวจ network, WAL, replica resource"
          runbook_url: "http://gridcare-infra/runbooks/C08-replication-lag-slot-failover.md"

      - alert: PostgresReplicationSlotInactive
        expr: pg_replication_slots_active == 0
        for: 10m
        labels: {severity: warning, owner: dba}
        annotations:
          summary: "Replication Slot {{ $labels.slot_name }} Inactive"
          description: "ตรวจ Replica, network, WAL"
          runbook_url: "http://gridcare-infra/runbooks/C08-replication-lag-slot-failover.md"

      - alert: PostgresReplicationWalAtRisk
        expr: pg_replication_slots_pg_wal_status{wal_status="unreserved"} == 1
        for: 5m
        labels: {severity: critical, owner: dba}
        annotations:
          summary: "Slot {{ $labels.slot_name }} WAL At Risk"
          description: "WAL ใกล้จะถูกเก็บ ต้องตรวจ Slot ทันที"
          runbook_url: "http://gridcare-infra/runbooks/C08-replication-lag-slot-failover.md"
```

### 10.2 ตรวจสอบ Metric

```bash
curl -s localhost:9187/metrics | grep -E 'patroni_primary|pg_stat_replication|pg_replication_slots'
```

### 10.3 ตรวจ Alert

```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

ผลลัพธ์:
```text
"alertname": "PatroniPrimaryCountNotOne",
"state": "firing"
```

### 10.4 ตรวจ HAProxy Stats

```bash
curl -s "http://127.0.0.1:7000/;csv" | awk -F, '$1=="primary" || $1=="replicas" {print $1, $2, $18}'
```

ผลลัพธ์:
```text
primary pg1 UP
primary pg2 DOWN
replicas pg1 DOWN
replicas pg2 UP
```

### 10.5 Dashboard HA Panel

| Panel | PromQL |
|---|---|
| Primary Count | `sum by (scope) (patroni_primary)` |
| Replication Lag | `max by (instance, application_name) (pg_stat_replication_pg_wal_lsn_diff)` |
| Slot Active | `pg_replication_slots_active` |
| Slot Status | `pg_replication_slots_pg_wal_status` |
| HAProxy UP | `haproxy_server_up` |

### 10.6 Prometheus Scrape Config

```yaml
- job_name: patroni
  static_configs:
    - targets: ['pg1:8008', 'pg2:8008']
```

## 11. ตัวอย่าง

### ตัวอย่างที่ 1: Alert `PatroniPrimaryCountNotOne`

```yaml
- alert: PatroniPrimaryCountNotOne
  expr: sum by (scope) (patroni_primary) != 1
  for: 1m
  labels: {severity: critical, owner: dba}
  annotations:
    summary: "คลัสเตอร์ {{ $labels.scope }} มี Primary {{ $value }} ตัว"
    runbook_url: "http://gridcare-infra/runbooks/C08-replication-lag-slot-failover.md"
```

### ตัวอย่างที่ 2: Alert `PostgresReplicationLagHigh`

```yaml
- alert: PostgresReplicationLagHigh
  expr: max by (instance, application_name) (pg_stat_replication_pg_wal_lsn_diff) > 100 * 1024 * 1024
  for: 5m
  labels: {severity: warning, owner: dba}
  annotations:
    summary: "Replication Lag > 100 MB"
```

### ตัวอย่างที่ 3: ตรวจสอบ Metric

```bash
curl -s localhost:9090/api/v1/query?query=sum%20by%20(scope)%20(patroni_primary) | python3 -m json.tool | grep -A2 '"value"'
```

ผลลัพธ์:
```text
"value": [
  1730702112.345,
  "1"
]
```

### ตัวอย่างที่ 4: ตรวจ HAProxy

```bash
curl -s "http://127.0.0.1:7000/;csv" | awk -F, '$1=="primary" || $1=="replicas" {print $1, $2, $18}'
```

ผลลัพธ์:
```text
primary pg1 UP
primary pg2 DOWN
replicas pg1 DOWN
replicas pg2 UP
```

### ตัวอย่างที่ 5: Unit Test

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
```

```bash
promtool test rules ~/gridcare-ha-alerts.test.yml
```

ผลลัพธ์:
```text
Unit Testing:  /home/student/gridcare-ha-alerts.test.yml
  SUCCESS
```

## 12. สรุปย่อ จำง่าย
- **`PatroniPrimaryCountNotOne` = Critical**  
- **`PostgresReplicationLagHigh` = Warning**  
- **`PostgresReplicationSlotInactive` = Warning**  
- **`PostgresReplicationWalAtRisk` = Critical**  
- **`patroni_primary` ต้องมี**  
- **ทดสอบด้วย `promtool test rules`**

ประโยคจำ: **"HA ที่ดีคือ HA ที่ทุก Metric ถูก Monitor และทุก Alert มี Runbook"**

## 13. แหล่งที่มาและแหล่งอ้างอิง
- Patroni — Metrics: https://patroni.readthedocs.io/en/latest/
- Prometheus Alerting Rules: https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/
- GridCare Workshop Day 4: Workshop Day 4 ขั้นที่ 1

---

## สรุปส่วนที่ 8 (บทที่ 71–80)

| บท | แก่นของบท | ใช้ต่อในส่วน |
|---|---|---|
| 71 | Streaming Replication | HA |
| 72 | Replication Slots | HA |
| 73 | Patroni และ etcd | HA |
| 74 | HAProxy | HA |
| 75 | PgBouncer | Performance, HA |
| 76 | Switchover | HA |
| 77 | Failover | HA, Game Day |
| 78 | Split-Brain | HA |
| 79 | pg_rewind | HA |
| 80 | HA Monitoring และ Alert | Monitoring |

---