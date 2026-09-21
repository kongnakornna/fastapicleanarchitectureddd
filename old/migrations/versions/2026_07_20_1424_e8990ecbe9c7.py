"""
Revision Message: add_username_and_status

Revision ID: e8990ecbe9c7
Revises: 0a4bcd898bd2
Create Date: 2026-07-20 14:24:53.861616

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e8990ecbe9c7'
down_revision: Union[str, Sequence[str], None] = '0a4bcd898bd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE user_status_enum AS ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED')")
    op.add_column('app_users', sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED', name='user_status_enum', create_type=False), nullable=False, server_default='ACTIVE', comment='Status of the user (active, inactive, suspended)'))
    op.add_column('app_users', sa.Column('username', sa.String(length=100), nullable=True, comment='Unique username of the user'))
    op.execute("UPDATE app_users SET username = 'admin' WHERE username IS NULL")
    op.alter_column('app_users', 'username', nullable=False)
    op.drop_constraint('uq_users_email_is_active', 'app_users', type_='unique')
    op.create_unique_constraint('uq_users_email_status', 'app_users', ['email', 'status'])
    op.create_unique_constraint('uq_users_username_status', 'app_users', ['username', 'status'])


def downgrade() -> None:
    op.drop_constraint('uq_users_username_status', 'app_users', type_='unique')
    op.drop_constraint('uq_users_email_status', 'app_users', type_='unique')
    op.create_unique_constraint('uq_users_email_is_active', 'app_users', ['email', 'is_active'])
    op.drop_column('app_users', 'username')
    op.drop_column('app_users', 'status')
    op.execute("DROP TYPE IF EXISTS user_status_enum")
