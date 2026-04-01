from sqlalchemy import Column, Integer, Boolean, DateTime, String, Text, ForeignKey, UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime, timezone
from uuid import uuid4, UUID as UUIDV4
from .base import Base


class MusicTrack(Base):
    """An uploaded audio file owned by a skater."""

    __tablename__ = 'm_tracks'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)

    uSkaterUUID = Column(UUID, ForeignKey("uSkaterConfig.uSkaterUUID", ondelete='CASCADE'),
                         nullable=False)

    title = Column(String, nullable=False)
    artist = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    is_performance_cut = Column(Boolean, default=False)
    cut_duration_seconds = Column(Integer, nullable=True)

    storage_key = Column(String, nullable=True)

    clearance_status = Column(String, nullable=False, default="not_required")
    clearance_provider = Column(String, nullable=True)
    clearance_ref = Column(String, nullable=True)

    apple_music_url = Column(String, nullable=True)
    spotify_url = Column(String, nullable=True)
    youtube_url = Column(String, nullable=True)

    created_at = Column(DateTime, nullable=False,
                        default=lambda: datetime.now(timezone.utc))

    playlist_entries = relationship("MusicPlaylistTrack", back_populates="track",
                                   cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, title, uSkaterUUID, artist=None, duration_seconds=None,
                 is_performance_cut=False, cut_duration_seconds=None,
                 storage_key=None, clearance_status="not_required",
                 clearance_provider=None, clearance_ref=None,
                 apple_music_url=None, spotify_url=None, youtube_url=None,
                 created_at=None):
        self.title = title
        self.uSkaterUUID = uSkaterUUID
        self.artist = artist
        self.duration_seconds = duration_seconds
        self.is_performance_cut = is_performance_cut
        self.cut_duration_seconds = cut_duration_seconds
        self.storage_key = storage_key
        self.clearance_status = clearance_status
        self.clearance_provider = clearance_provider
        self.clearance_ref = clearance_ref
        self.apple_music_url = apple_music_url
        self.spotify_url = spotify_url
        self.youtube_url = youtube_url
        self.created_at = created_at or datetime.now(timezone.utc)

    def __repr__(self):
        return f"<MusicTrack({self.title}, {self.artist})>"


class MusicPlaylist(Base):
    """A named collection of tracks owned by a skater."""

    __tablename__ = 'm_playlists'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)

    uSkaterUUID = Column(UUID, ForeignKey("uSkaterConfig.uSkaterUUID", ondelete='CASCADE'),
                         nullable=False)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    playlist_type = Column(String, nullable=False, default="practice")

    share_token = Column(UUID, nullable=True, unique=True)

    created_at = Column(DateTime, nullable=False,
                        default=lambda: datetime.now(timezone.utc))

    track_entries = relationship("MusicPlaylistTrack", back_populates="playlist",
                                cascade="all, delete-orphan", passive_deletes=True,
                                order_by="MusicPlaylistTrack.position")

    def __init__(self, name, uSkaterUUID, description=None,
                 playlist_type="practice", share_token=None, created_at=None):
        self.name = name
        self.uSkaterUUID = uSkaterUUID
        self.description = description
        self.playlist_type = playlist_type
        self.share_token = share_token
        self.created_at = created_at or datetime.now(timezone.utc)

    def __repr__(self):
        return f"<MusicPlaylist({self.name}, type={self.playlist_type})>"


class MusicPlaylistTrack(Base):
    """Join table linking tracks to playlists with ordering."""

    __tablename__ = 'm_playlist_tracks'
    __table_args__ = {'extend_existing': True}

    id: Mapped[UUIDV4] = mapped_column(primary_key=True, default=uuid4)

    playlist_id = Column(UUID, ForeignKey("m_playlists.id", ondelete='CASCADE'), nullable=False)
    track_id = Column(UUID, ForeignKey("m_tracks.id", ondelete='CASCADE'), nullable=False)
    position = Column(Integer, nullable=False, default=0)

    playlist = relationship("MusicPlaylist", back_populates="track_entries")
    track = relationship("MusicTrack", back_populates="playlist_entries")

    def __init__(self, playlist_id, track_id, position=0):
        self.playlist_id = playlist_id
        self.track_id = track_id
        self.position = position

    def __repr__(self):
        return f"<MusicPlaylistTrack(playlist={self.playlist_id}, track={self.track_id}, pos={self.position})>"
