"""Add password_reset_tokens table

Revision ID: 005_pw_reset
Revises: 004_invite_tokens
Create Date: 2026-03-03

Single-use, time-limited tokens for the forgot-password email flow.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005_pw_reset"
down_revision: Union[str, None] = "004_invite_tokens"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("token", sa.String(64), unique=True, nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("uAuthTable.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime, nullable=False),
        sa.Column("used", sa.Boolean, nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_table("password_reset_tokens")
