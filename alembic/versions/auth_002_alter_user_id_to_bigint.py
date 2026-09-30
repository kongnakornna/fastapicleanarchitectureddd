"""alter erp_authentications.user_id from UUID to BIGINT

Revision ID: auth_002
Revises: auth_001
Create Date: 2026-09-28
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# ⚠️ แก้ตรงนี้ให้ตรงกับ revision ของคุณ
revision = "auth_002"
down_revision = "auth_001"
branch_labels = None
depends_on = None

TABLE = "erp_authentications"
USERS_TABLE = "erp_users"


def upgrade() -> None:
    conn = op.get_bind()

    # ── 1) เช็ค row count — ถ้ามีข้อมูล ต้องเคลียร์ก่อน ─────────────
    count = conn.execute(
        sa.text(f"SELECT COUNT(*) FROM {TABLE}")
    ).scalar()

    if count and count > 0:
        # ⚠️ auth sessions ลบทิ้งได้ (users จะ login ใหม่) — ปลอดภัย
        # แต่ถ้าไม่อยากลบ ให้เปลี่ยน conversion logic ด้านล่าง
        op.execute(sa.text(f"TRUNCATE TABLE {TABLE} RESTART IDENTITY CASCADE"))

    # ── 2) Drop FK constraint (ถ้ามี) ────────────────────────────
    # ชื่อ constraint จริงอาจต่าง — ดูจาก DB หรือถ้าไม่รู้ก็ปล่อยผ่าน
    op.execute(sa.text(
        f"""DO $$
        DECLARE
            fk_name TEXT;
        BEGIN
            SELECT tc.constraint_name INTO fk_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = '{TABLE}'
              AND tc.constraint_type = 'FOREIGN KEY'
              AND kcu.column_name = 'user_id';

            IF fk_name IS NOT NULL THEN
                EXECUTE 'ALTER TABLE {TABLE} DROP CONSTRAINT ' || fk_name;
            END IF;
        END $$;"""
    ))

    # ── 3) Alter column type: UUID → BIGINT ──────────────────────
    op.alter_column(
        TABLE,
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.BigInteger(),
        existing_nullable=False,
        postgresql_using="user_id::text::bigint",  # ⚠️ ใช้ได้เฉพาะกรณี value เป็นตัวเลข
    )

    # ── 4) Re-create FK → erp_users.id ───────────────────────────
    op.create_foreign_key(
        f"{TABLE}_user_id_fkey",
        TABLE,
        USERS_TABLE,
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # ── 5) Ensure index exists ────────────────────────────────────
    op.execute(sa.text(
        f"""CREATE INDEX IF NOT EXISTS
            ix_{TABLE}_user_id_user_agent_device
            ON {TABLE} (user_id, user_agent, device)"""
    ))


def downgrade() -> None:
    # ย้อนกลับ — ทำได้แค่ถ้า table ว่าง (เพราะ BIGINT → UUID ไม่ reversible)
    op.drop_constraint(f"{TABLE}_user_id_fkey", TABLE, type_="foreignkey")
    op.alter_column(
        TABLE,
        "user_id",
        existing_type=sa.BigInteger(),
        type_=postgresql.UUID(as_uuid=True),
        existing_nullable=False,
        postgresql_using="gen_random_uuid()",
    )
    op.create_foreign_key(
        f"{TABLE}_user_id_fkey",
        TABLE,
        USERS_TABLE,
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
