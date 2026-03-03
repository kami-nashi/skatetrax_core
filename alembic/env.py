"""
Alembic environment. Builds the database URL from PGDB_* environment variables
(same as skatetrax.models.cyberconnect2). Run with those set for dev or prod.
"""
import os
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from alembic import context

# Import Base and all models so target_metadata is complete (for autogenerate).
from skatetrax.models.base import Base
from skatetrax.models import (
    t_auth,
    t_equip,
    t_skaterMeta,
    t_ice_time,
    t_icetype,
    t_locations,
    t_maint,
    t_memberships,
    t_coaches,
    t_classes,
    t_events,
    t_tests,
    t_journal,
)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    """Build PostgreSQL URL from PGDB_* env vars (same as app)."""
    host = os.environ.get("PGDB_HOST", "localhost")
    name = os.environ.get("PGDB_NAME", "skatetrax")
    user = os.environ.get("PGDB_USER", "postgres")
    password = os.environ.get("PGDB_PASSWORD", "")
    url = f"postgresql://{user}:{password}@{host}/{name}"
    # Avoid GSSAPI/Kerberos (e.g. on Fedora/RHEL); DO and local use password auth.
    params = ["gssencmode=disable"]
    sslmode = os.environ.get("PGDB_SSLMODE")
    if sslmode:
        params.append(f"sslmode={sslmode}")
    return f"{url}?{'&'.join(params)}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (SQL only, no live DB)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connects to DB)."""
    connectable = create_engine(get_url(), poolclass=NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
