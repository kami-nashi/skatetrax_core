"""Drop legacy role storage

Revision ID: 006_drop_legacy_roles
Revises: 005_pw_reset
Create Date: 2026-03-03

Removes the uSkaterRoles JSONB column from uSkaterConfig and drops the
u_skater_types lookup table.  Both are superseded by the role + user_roles
tables added in migration 003.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "006_drop_legacy_roles"
down_revision: Union[str, None] = "005_pw_reset"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("uSkaterConfig", "uSkaterRoles")
    op.execute('DROP TABLE IF EXISTS u_skater_types')


def downgrade() -> None:
    op.add_column(
        "uSkaterConfig",
        sa.Column("uSkaterRoles", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
    )
    op.execute("""
        CREATE TABLE IF NOT EXISTS u_skater_types (
            id INTEGER PRIMARY KEY,
            label VARCHAR
        )
    """)
