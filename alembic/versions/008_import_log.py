"""Add import log table

Revision ID: 008_import_log
Revises: 007_competition_results_schema
Create Date: 2026-03-04

Adds e_import_log for auditing URL-based results imports.
Tracks source URL, match status, linked event/entry, and raw HTML
for debugging failed imports.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "008_import_log"
down_revision: Union[str, None] = "007_competition_results_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "e_import_log",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("source_url", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False, server_default="usfsa_6.0"),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("skater_name_searched", sa.String(), nullable=False),
        sa.Column("skater_name_matched", sa.String(), nullable=True),
        sa.Column("event_id", sa.UUID(),
                  sa.ForeignKey("e_events.id", ondelete="SET NULL"), nullable=True),
        sa.Column("entry_id", sa.UUID(),
                  sa.ForeignKey("e_event_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("raw_html", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("uSkaterUUID", sa.UUID(),
                  sa.ForeignKey("uSkaterConfig.uSkaterUUID", ondelete="CASCADE"),
                  nullable=False),
    )


def downgrade() -> None:
    op.drop_table("e_import_log")
