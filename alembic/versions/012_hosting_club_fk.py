"""Convert hosting_club from String to UUID FK

Revision ID: 012_hosting_club_fk
Revises: 011_entry_status_column
Create Date: 2026-03-05

Changes hosting_club on e_events from a plain VARCHAR to a UUID column
with a foreign key constraint referencing club_directory.club_id.
Existing varchar values are cast to UUID; any that fail to cast are set
to NULL.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '012_hosting_club_fk'
down_revision: Union[str, None] = '011_entry_status_column'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE e_events SET hosting_club = NULL
        WHERE hosting_club IS NOT NULL
          AND hosting_club::text NOT IN (SELECT club_id::text FROM club_directory)
    """)
    op.execute("""
        ALTER TABLE e_events
        ALTER COLUMN hosting_club TYPE UUID USING hosting_club::uuid
    """)
    op.create_foreign_key(
        'fk_e_events_hosting_club',
        'e_events', 'club_directory',
        ['hosting_club'], ['club_id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_e_events_hosting_club', 'e_events', type_='foreignkey')
    op.execute("""
        ALTER TABLE e_events
        ALTER COLUMN hosting_club TYPE VARCHAR USING hosting_club::text
    """)
