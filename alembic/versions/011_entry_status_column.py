"""Add status column to event entries

Revision ID: 011_entry_status_column
Revises: 010_rename_cjs_composition
Create Date: 2026-03-04

Adds a non-nullable status column to e_event_entries with a default of
'Committed'.  Existing rows are backfilled to 'Scored' since they all
have competition results already recorded.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '011_entry_status_column'
down_revision: Union[str, None] = '010_rename_cjs_composition'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'e_event_entries',
        sa.Column('status', sa.String(), nullable=False, server_default='Committed'),
    )
    op.execute("UPDATE e_event_entries SET status = 'Scored'")


def downgrade() -> None:
    op.drop_column('e_event_entries', 'status')
