"""Add invite_tokens table for invite-only beta registration

Revision ID: 004_invite_tokens
Revises: 003_role_tables
Create Date: 2026-03-01

Supports single-use and multi-use invite tokens distributed via
NFC tags, QR codes, or direct links.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004_invite_tokens"
down_revision: Union[str, None] = "003_role_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "invite_tokens",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("token", sa.String(64), unique=True, nullable=False),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("uAuthTable.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("max_uses", sa.Integer, nullable=False, server_default="1"),
        sa.Column("use_count", sa.Integer, nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("invite_tokens")
