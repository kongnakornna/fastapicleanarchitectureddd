"""
Revision Message: make origin and referrer nullable in sessions

Revision ID: a9a05a7f432d
Revises: 25845428d7a7
Create Date: 2026-07-20 22:56:33.214810

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a9a05a7f432d'
down_revision: Union[str, Sequence[str], None] = '25845428d7a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('app_sessions', 'origin',
               existing_type=sa.VARCHAR(length=255),
               nullable=True,
               existing_comment='Origin header value of the client')
    op.alter_column('app_sessions', 'referrer',
               existing_type=sa.VARCHAR(length=255),
               nullable=True,
               existing_comment='Referrer header value of the client')


def downgrade() -> None:
    op.alter_column('app_sessions', 'referrer',
               existing_type=sa.VARCHAR(length=255),
               nullable=False,
               existing_comment='Referrer header value of the client')
    op.alter_column('app_sessions', 'origin',
               existing_type=sa.VARCHAR(length=255),
               nullable=False,
               existing_comment='Origin header value of the client')
