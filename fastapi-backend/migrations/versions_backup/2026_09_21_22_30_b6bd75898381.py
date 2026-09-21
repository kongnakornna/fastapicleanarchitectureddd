"""
Revision Message: merge heads

Revision ID: b6bd75898381
Revises: e8c09cdc7746, a1b2c3d4e5f6
Create Date: 2026-09-21 22:30:12.687669

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision: str = 'b6bd75898381'
down_revision: Union[str, Sequence[str], None] = ('e8c09cdc7746', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
