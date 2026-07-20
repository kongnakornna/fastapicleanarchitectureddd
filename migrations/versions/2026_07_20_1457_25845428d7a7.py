"""
Revision Message: add_permission_tables

Revision ID: 25845428d7a7
Revises: e8990ecbe9c7
Create Date: 2026-07-20 14:57:28.896854

"""

from typing import Sequence, Union

from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision: str = '25845428d7a7'
down_revision: Union[str, Sequence[str], None] = 'e8990ecbe9c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('app_permissions',
    sa.Column('name', sa.String(length=100), nullable=False, comment='Name of the permission'),
    sa.Column('description', sa.Text(), nullable=True, comment='Description of the permission'),
    sa.Column('resource', sa.String(length=100), nullable=False, comment="Resource that the permission applies to (e.g. 'user', 'session')"),
    sa.Column('action', sa.String(length=50), nullable=False, comment="Action allowed on the resource (e.g. 'create', 'read', 'update', 'delete')"),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier of the record'),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('app_roles',
    sa.Column('name', sa.String(length=100), nullable=False, comment='Name of the role'),
    sa.Column('description', sa.Text(), nullable=True, comment='Description of the role'),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier of the record'),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('app_role_permissions',
    sa.Column('role_id', sa.UUID(), nullable=False, comment='Identifier of the role'),
    sa.Column('permission_id', sa.UUID(), nullable=False, comment='Identifier of the permission'),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier of the record'),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
    sa.ForeignKeyConstraint(['permission_id'], ['app_permissions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_id'], ['app_roles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('role_id', 'permission_id', name='uq_role_permissions')
    )
    op.create_table('app_user_roles',
    sa.Column('user_id', sa.UUID(), nullable=False, comment='Identifier of the user'),
    sa.Column('role_id', sa.UUID(), nullable=False, comment='Identifier of the role'),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier of the record'),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
    sa.ForeignKeyConstraint(['role_id'], ['app_roles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['app_users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'role_id', name='uq_user_roles')
    )

    # Seed default roles
    admin_id = str(uuid4())
    manager_id = str(uuid4())
    user_id = str(uuid4())

    op.execute(
        f"INSERT INTO app_roles (id, name, description, is_active, created_at, updated_at) VALUES "
        f"('{admin_id}', 'admin', 'Administrator role with full access', true, now(), now()), "
        f"('{manager_id}', 'manager', 'Manager role with elevated access', true, now(), now()), "
        f"('{user_id}', 'user', 'Regular user role with basic access', true, now(), now())"
    )


def downgrade() -> None:
    op.drop_table('app_user_roles')
    op.drop_table('app_role_permissions')
    op.drop_table('app_roles')
    op.drop_table('app_permissions')
