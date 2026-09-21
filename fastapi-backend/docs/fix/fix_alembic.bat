# 1. ตรวจสอบ revision ปัจจุบัน
uv run alembic current
# ควรแสดง revision (เช่น abc123def456 (head))

# 2. ตรวจสอบ head revision
uv run alembic heads
# ควรแสดง revision เดียวกัน

# 3. ตรวจสอบว่ามี pending migrations
uv run alembic check
# ควรแสดง "No new upgrade operations detected."

# 4. ตรวจสอบตารางใน DB
psql -h localhost -p 5437 -U postgres -d ioterp -c "\dt"
# ควรเห็น alembic_version + tables จาก models

# 5. ตรวจสอบ alembic_version
psql -h localhost -p 5437 -U postgres -d ioterp -c "SELECT * FROM alembic_version;"
# ควรมี 1 row ที่ตรงกับ head revision