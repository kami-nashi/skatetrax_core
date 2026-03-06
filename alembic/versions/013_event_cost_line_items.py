"""Replace event_cost column with e_event_costs line-item table.

Revision ID: 013_event_cost_line_items
Revises: 012_hosting_club_fk
Create Date: 2026-03-05

1. Creates e_event_costs table.
2. Migrates existing event_cost values into a single "Competition Entry"
   line item per event.
3. Drops the event_cost column from e_events.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '013_event_cost_line_items'
down_revision: Union[str, None] = '012_hosting_club_fk'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'e_event_costs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('event_id', UUID(as_uuid=True),
                  sa.ForeignKey('e_events.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('note', sa.String(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
    )

    op.execute("""
        INSERT INTO e_event_costs (id, event_id, category, note, amount, quantity)
        SELECT gen_random_uuid(), id, 'Competition Entry',
               'Migrated from event_cost', event_cost, 1
        FROM e_events
        WHERE event_cost IS NOT NULL AND event_cost > 0
    """)

    op.drop_column('e_events', 'event_cost')


def downgrade() -> None:
    op.add_column('e_events',
                  sa.Column('event_cost', sa.Float(), server_default='0.0'))

    op.execute("""
        UPDATE e_events SET event_cost = COALESCE(
            (SELECT SUM(amount * quantity) FROM e_event_costs
             WHERE e_event_costs.event_id = e_events.id), 0)
    """)

    op.drop_table('e_event_costs')
