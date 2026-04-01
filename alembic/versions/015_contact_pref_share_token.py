"""Add contact_preference and share_token to uSkaterConfig.

Revision ID: 015_contact_pref_share_token
Revises: 014_music_tables
Create Date: 2026-03-31
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '015_contact_pref_share_token'
down_revision: Union[str, None] = '014_music_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('uSkaterConfig',
                  sa.Column('contact_preference', sa.String(), nullable=True,
                            server_default='email'))
    op.add_column('uSkaterConfig',
                  sa.Column('share_token', UUID(as_uuid=True), nullable=True))
    op.create_unique_constraint('uq_skater_share_token', 'uSkaterConfig', ['share_token'])
    op.execute("UPDATE \"uSkaterConfig\" SET contact_preference = 'email' WHERE contact_preference IS NULL")


def downgrade() -> None:
    op.drop_constraint('uq_skater_share_token', 'uSkaterConfig', type_='unique')
    op.drop_column('uSkaterConfig', 'share_token')
    op.drop_column('uSkaterConfig', 'contact_preference')
