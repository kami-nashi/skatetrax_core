"""
Auth service layer -- pure data operations with no Flask dependency.
All functions use create_session() for short-lived DB access and return
detached (expunged) model instances.
"""
from skatetrax.models.cyberconnect2 import create_session
from skatetrax.models.t_auth import (
    uAuthTable, Role, UserRoles, InviteToken, PasswordResetToken,
)


# ---------------------------------------------------------------------------
# User operations
# ---------------------------------------------------------------------------

def find_user(identifier=None, **kwargs):
    """Look up a user by id, aLogin, aEmail, or fs_uniquifier."""
    if identifier is None and not kwargs:
        return None
    with create_session() as db:
        user = None
        if identifier is not None:
            try:
                uid = int(identifier)
                user = db.query(uAuthTable).filter_by(id=uid).first()
            except (ValueError, TypeError):
                pass
            if user is None:
                user = db.query(uAuthTable).filter_by(aLogin=identifier).first()
            if user is None:
                user = db.query(uAuthTable).filter_by(aEmail=identifier).first()
        if user is None and kwargs:
            if "fs_uniquifier" in kwargs:
                user = db.query(uAuthTable).filter_by(fs_uniquifier=kwargs["fs_uniquifier"]).first()
            elif "aLogin" in kwargs:
                user = db.query(uAuthTable).filter_by(aLogin=kwargs["aLogin"]).first()
            elif "aEmail" in kwargs:
                user = db.query(uAuthTable).filter_by(aEmail=kwargs["aEmail"]).first()
        if user is not None:
            db.expunge(user)
        return user


def get_user(id_or_email):
    """Load user by id (str or int), aLogin, or aEmail."""
    if id_or_email is None:
        return None
    with create_session() as db:
        try:
            uid = int(id_or_email)
            user = db.query(uAuthTable).filter_by(id=uid).first()
        except (ValueError, TypeError):
            user = (
                db.query(uAuthTable).filter_by(aLogin=id_or_email).first()
                or db.query(uAuthTable).filter_by(aEmail=id_or_email).first()
            )
        if user is not None:
            db.expunge(user)
        return user


def create_user(aLogin=None, aEmail=None, password=None, phone_number=None, **kwargs):
    """Create a new uAuthTable row and return the detached instance."""
    email = kwargs.pop("email", aEmail)
    login = kwargs.pop("username", aLogin)
    if email is None or login is None:
        raise ValueError("aLogin and aEmail (or email/username) required")
    with create_session() as db:
        user = uAuthTable(
            aLogin=login,
            aEmail=email,
            phone_number=phone_number or kwargs.pop("phone_number", None),
        )
        user.set_password(password or kwargs.pop("password", ""))
        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)
        return user


def update_password(user_or_id, new_password):
    """Hash and persist a new password for the given user."""
    user_id = user_or_id.id if hasattr(user_or_id, "id") else int(user_or_id)
    with create_session() as db:
        db_user = db.query(uAuthTable).filter_by(id=user_id).first()
        if db_user is None:
            return False
        db_user.set_password(new_password)
        db.commit()
        return True


# ---------------------------------------------------------------------------
# Role operations
# ---------------------------------------------------------------------------

def find_role(role_name):
    with create_session() as db:
        role = db.query(Role).filter_by(name=role_name).first()
        if role is not None:
            db.expunge(role)
        return role


def create_role(**kwargs):
    with create_session() as db:
        role = Role(**kwargs)
        db.add(role)
        db.commit()
        db.refresh(role)
        db.expunge(role)
        return role


def add_role_to_user(user_or_id, role_name):
    """Assign a role (by name) to a user. Returns True if added, False if already present."""
    user_id = user_or_id.id if hasattr(user_or_id, "id") else int(user_or_id)
    role = find_role(role_name) if isinstance(role_name, str) else role_name
    if role is None:
        return False
    with create_session() as db:
        exists = db.query(UserRoles).filter_by(user_id=user_id, role_id=role.id).first()
        if exists:
            return False
        db.add(UserRoles(user_id=user_id, role_id=role.id))
        db.commit()
        return True


def remove_role_from_user(user_or_id, role_name):
    user_id = user_or_id.id if hasattr(user_or_id, "id") else int(user_or_id)
    role = find_role(role_name) if isinstance(role_name, str) else role_name
    if role is None:
        return False
    with create_session() as db:
        link = db.query(UserRoles).filter_by(user_id=user_id, role_id=role.id).first()
        if link is None:
            return False
        db.delete(link)
        db.commit()
        return True


def get_user_roles(user_or_id):
    user_id = user_or_id.id if hasattr(user_or_id, "id") else int(user_or_id)
    with create_session() as db:
        roles = db.query(Role).join(UserRoles).filter(UserRoles.user_id == user_id).all()
        for r in roles:
            db.expunge(r)
        return roles


# ---------------------------------------------------------------------------
# Invite token operations
# ---------------------------------------------------------------------------

def validate_invite_token(token_str):
    """Return the InviteToken if valid, else None."""
    with create_session() as db:
        token = db.query(InviteToken).filter_by(token=token_str).first()
        if token is None or not token.is_valid():
            return None
        db.expunge(token)
        return token


def consume_invite_token(token_str):
    """Increment use_count. Returns True on success, False if invalid."""
    with create_session() as db:
        token = db.query(InviteToken).filter_by(token=token_str).first()
        if token is None or not token.is_valid():
            return False
        token.use_count += 1
        db.commit()
        return True


def create_invite_token(created_by=None, max_uses=1, expires_at=None):
    with create_session() as db:
        token = InviteToken(
            created_by=created_by,
            max_uses=max_uses,
            expires_at=expires_at,
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        db.expunge(token)
        return token


# ---------------------------------------------------------------------------
# Password-reset token operations
# ---------------------------------------------------------------------------

def create_reset_token(user_id):
    with create_session() as db:
        token = PasswordResetToken(user_id=user_id)
        db.add(token)
        db.commit()
        db.refresh(token)
        db.expunge(token)
        return token


def validate_reset_token(token_str):
    with create_session() as db:
        token = db.query(PasswordResetToken).filter_by(token=token_str).first()
        if token is None or not token.is_valid():
            return None
        db.expunge(token)
        return token


def consume_reset_token(token_str):
    with create_session() as db:
        token = db.query(PasswordResetToken).filter_by(token=token_str).first()
        if token is None:
            return False
        token.used = True
        db.commit()
        return True
