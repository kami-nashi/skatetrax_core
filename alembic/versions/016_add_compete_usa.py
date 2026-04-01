"""Add Compete USA governing body and event types.

Revision ID: 016_add_compete_usa
Revises: 015_contact_pref_share_token
"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = '016_add_compete_usa'
down_revision: Union[str, None] = '015_contact_pref_share_token'
branch_labels: Union[str, None] = None
depends_on: Union[str, None] = None

COMPETE_USA_GB_ID = "a0000000-0000-0000-0000-000000000005"

EVENT_TYPES = [
    ("b0000000-0000-0000-0000-000000000007", "Competition", "6.0",  COMPETE_USA_GB_ID, True),
    ("b0000000-0000-0000-0000-000000000008", "Competition", "6.0",  COMPETE_USA_GB_ID, False),
    ("b0000000-0000-0000-0000-000000000009", "Competition", "IJS",  COMPETE_USA_GB_ID, False),
    ("b0000000-0000-0000-0000-00000000000a", "Competition", "CJS",  COMPETE_USA_GB_ID, False),
]


def upgrade() -> None:
    gb_table = sa.table(
        "e_governing_bodies",
        sa.column("id", sa.UUID),
        sa.column("short_name", sa.String),
        sa.column("full_name", sa.String),
    )
    op.bulk_insert(gb_table, [
        {"id": COMPETE_USA_GB_ID, "short_name": "Compete USA", "full_name": "Compete USA"},
    ])

    et_table = sa.table(
        "e_event_types",
        sa.column("id", sa.UUID),
        sa.column("category", sa.String),
        sa.column("scoring_system", sa.String),
        sa.column("governing_body_id", sa.UUID),
        sa.column("single_mark", sa.Boolean),
    )
    op.bulk_insert(et_table, [
        {"id": uid, "category": cat, "scoring_system": ss,
         "governing_body_id": gb, "single_mark": sm}
        for uid, cat, ss, gb, sm in EVENT_TYPES
    ])


def downgrade() -> None:
    op.execute(
        f"DELETE FROM e_event_types WHERE governing_body_id = '{COMPETE_USA_GB_ID}'"
    )
    op.execute(
        f"DELETE FROM e_governing_bodies WHERE id = '{COMPETE_USA_GB_ID}'"
    )
