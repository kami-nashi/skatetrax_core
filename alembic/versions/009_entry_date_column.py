"""Add entry_date to event entries

Revision ID: 009_entry_date_column
Revises: 008_import_log
Create Date: 2026-03-01

Adds a nullable entry_date column to e_event_entries so individual
segments can record their own date within a multi-day competition.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '009_entry_date_column'
down_revision: Union[str, None] = '008_import_log'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('e_event_entries', sa.Column('entry_date', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('e_event_entries', 'entry_date')
