"""Add role and user_roles tables; migrate JSONB roles

Revision ID: 003_role_tables
Revises: 002_fs_uniquifier
Create Date: 2026-03-01

Creates the FST-compatible role and user_roles tables. Seeds role rows
from existing u_skater_types, then migrates each user's
uSkaterConfig.uSkaterRoles JSONB array into user_roles junction rows.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003_role_tables"
down_revision: Union[str, None] = "002_fs_uniquifier"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create role table
    op.create_table(
        "role",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(80), unique=True, nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
    )

    # 2. Create user_roles junction table
    op.create_table(
        "user_roles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("uAuthTable.id"), nullable=False),
        sa.Column("role_id", sa.Integer, sa.ForeignKey("role.id"), nullable=False),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_roles"),
    )

    # 3. Seed role from u_skater_types (1=Adult, 2=Coach, 3=Minor, 4=Guardian)
    op.execute("""
        INSERT INTO role (id, name, description)
        SELECT id, lower(label), label
        FROM u_skater_types
        ON CONFLICT DO NOTHING
    """)

    # 4. Migrate JSONB role assignments into user_roles.
    #    uSkaterConfig.uSkaterRoles is a JSONB array of ints referencing u_skater_types.id.
    #    Join via uSkaterUUID to get the uAuthTable.id for user_id.
    op.execute("""
        INSERT INTO user_roles (user_id, role_id)
        SELECT a.id, r.value::int
        FROM "uSkaterConfig" sc,
             jsonb_array_elements(sc."uSkaterRoles") AS r(value),
             "uAuthTable" a
        WHERE a."uSkaterUUID" = sc."uSkaterUUID"
          AND r.value::int IN (SELECT id FROM role)
        ON CONFLICT ON CONSTRAINT uq_user_roles DO NOTHING
    """)


def downgrade() -> None:
    op.drop_table("user_roles")
    op.drop_table("role")
