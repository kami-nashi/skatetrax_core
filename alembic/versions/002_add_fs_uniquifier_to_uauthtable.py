"""Add fs_uniquifier column to uAuthTable

Revision ID: 002_fs_uniquifier
Revises: 001_equip_fk
Create Date: 2026-03-01

Flask-Security-Too 4.0+ requires fs_uniquifier on the user model for
session token management. This is independent of uSkaterUUID, which
remains the data-aggregation key across all tables.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_fs_uniquifier"
down_revision: Union[str, None] = "001_equip_fk"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add as nullable so existing rows don't block the ALTER
    op.add_column(
        "uAuthTable",
        sa.Column("fs_uniquifier", sa.String(64), nullable=True),
    )

    # 2. Populate every existing row with a unique hex value
    op.execute(
        """
        UPDATE "uAuthTable"
        SET fs_uniquifier = replace(gen_random_uuid()::text, '-', '')
        WHERE fs_uniquifier IS NULL
        """
    )

    # 3. Now enforce NOT NULL and UNIQUE
    op.alter_column("uAuthTable", "fs_uniquifier", nullable=False)
    op.create_unique_constraint(
        "uq_uauthtable_fs_uniquifier", "uAuthTable", ["fs_uniquifier"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_uauthtable_fs_uniquifier", "uAuthTable", type_="unique")
    op.drop_column("uAuthTable", "fs_uniquifier")
