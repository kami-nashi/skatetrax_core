from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Boolean, Column, ForeignKey, String, Integer, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime, timedelta, timezone
from .base import Base

from uuid import uuid4


class Role(Base):
    """FST-compatible role table. Seeded from u_skater_types values."""
    __tablename__ = 'role'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    def get_permissions(self):
        return set()

    def __repr__(self):
        return f"<Role(name='{self.name}')>"


class UserRoles(Base):
    """Junction table: which users hold which roles."""
    __tablename__ = 'user_roles'
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_roles'),
        {'extend_existing': True},
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('uAuthTable.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)


class InviteToken(Base):
    """Invite-only beta gate. Tokens are distributed via NFC/QR/link."""
    __tablename__ = 'invite_tokens'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True, nullable=False, default=lambda: uuid4().hex)
    created_by = Column(Integer, ForeignKey('uAuthTable.id'), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    max_uses = Column(Integer, nullable=False, default=1)
    use_count = Column(Integer, nullable=False, default=0)

    def is_valid(self):
        if self.max_uses > 0 and self.use_count >= self.max_uses:
            return False
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            return False
        return True

    def __repr__(self):
        return f"<InviteToken(token='{self.token[:8]}...', uses={self.use_count}/{self.max_uses})>"


class PasswordResetToken(Base):
    """Time-limited, single-use token for forgot-password flow."""
    __tablename__ = 'password_reset_tokens'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True, nullable=False, default=lambda: uuid4().hex)
    user_id = Column(Integer, ForeignKey('uAuthTable.id'), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(hours=1))
    used = Column(Boolean, nullable=False, default=False)

    def is_valid(self):
        if self.used:
            return False
        if datetime.now(timezone.utc) > self.expires_at:
            return False
        return True

    def __repr__(self):
        return f"<PasswordResetToken(token='{self.token[:8]}...', used={self.used})>"


class uAuthTable(Base):
    __tablename__ = 'uAuthTable'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    
    # Username, Pass, Contact
    aLogin = Column(String(80), unique=True, nullable=False)
    aPasswordHash = Column(Text, nullable=False)
    aEmail = Column(String(120), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)

    uSkaterUUID = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)

    # Flask-Security-Too session uniquifier (independent of uSkaterUUID)
    fs_uniquifier = Column(String(64), unique=True, nullable=False, default=lambda: uuid4().hex)

    roles = relationship('Role', secondary='user_roles', lazy='joined')
    
    # Basic Logging
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def set_password(self, password):
        self.aPasswordHash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.aPasswordHash, password)

    def get_id(self):
        """Returns fs_uniquifier for Flask-Login / FST session management."""
        return str(self.fs_uniquifier)

    def has_role(self, role_name):
        return any(r.name == role_name for r in (self.roles or []))

    @property
    def active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    def __repr__(self):
        return f"<User(username='{self.aLogin}', email='{self.aEmail}')>"
