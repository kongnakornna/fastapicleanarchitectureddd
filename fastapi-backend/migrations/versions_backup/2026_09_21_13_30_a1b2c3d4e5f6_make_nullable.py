"""make user gender and birthdate nullable

Revision ID: a1b2c3d4e5f6
Revises: 7e826ae930fa
Create Date: 2026-09-21 13:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "7e826ae930fa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "erp_users",
        "gender",
        existing_type=sa.Enum(
            "MALE",
            "FEMALE",
            "NON_BINARY",
            "OTHER",
            name="gender_enum",
        ),
        nullable=True,
    )
    op.alter_column(
        "erp_users",
        "birthdate",
        existing_type=sa.Date(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "erp_users",
        "gender",
        existing_type=sa.Enum(
            "MALE",
            "FEMALE",
            "NON_BINARY",
            "OTHER",
            name="gender_enum",
        ),
        nullable=False,
    )
    op.alter_column(
        "erp_users",
        "birthdate",
        existing_type=sa.Date(),
        nullable=False,
    )
