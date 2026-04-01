"""Create music library tables (m_tracks, m_playlists, m_playlist_tracks).

Revision ID: 014_music_tables
Revises: 013_event_cost_line_items
Create Date: 2026-03-31
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '014_music_tables'
down_revision: Union[str, None] = '013_event_cost_line_items'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'm_tracks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('uSkaterUUID', UUID(as_uuid=True),
                  sa.ForeignKey('uSkaterConfig.uSkaterUUID', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('artist', sa.String(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('is_performance_cut', sa.Boolean(), server_default='false'),
        sa.Column('cut_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('storage_key', sa.String(), nullable=True),
        sa.Column('clearance_status', sa.String(), nullable=False,
                  server_default='not_required'),
        sa.Column('clearance_provider', sa.String(), nullable=True),
        sa.Column('clearance_ref', sa.String(), nullable=True),
        sa.Column('apple_music_url', sa.String(), nullable=True),
        sa.Column('spotify_url', sa.String(), nullable=True),
        sa.Column('youtube_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
    )

    op.create_table(
        'm_playlists',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('uSkaterUUID', UUID(as_uuid=True),
                  sa.ForeignKey('uSkaterConfig.uSkaterUUID', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('playlist_type', sa.String(), nullable=False,
                  server_default='practice'),
        sa.Column('share_token', UUID(as_uuid=True), nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
    )

    op.create_table(
        'm_playlist_tracks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('playlist_id', UUID(as_uuid=True),
                  sa.ForeignKey('m_playlists.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('track_id', UUID(as_uuid=True),
                  sa.ForeignKey('m_tracks.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.UniqueConstraint('playlist_id', 'track_id',
                            name='uq_playlist_track'),
    )


def downgrade() -> None:
    op.drop_table('m_playlist_tracks')
    op.drop_table('m_playlists')
    op.drop_table('m_tracks')
