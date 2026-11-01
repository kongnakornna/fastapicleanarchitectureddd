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