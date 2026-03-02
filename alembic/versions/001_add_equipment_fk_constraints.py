"""Add FK constraints on equipment uSkaterUUID columns

Revision ID: 001_equip_fk
Revises:
Create Date: 2026-03-01

Adds REFERENCES "uSkaterConfig"(uSkaterUUID) ON DELETE CASCADE to
uSkateConfig, uSkaterBlades, uSkaterBoots. Run equipment_fk_check_orphans.sql
first and fix any orphaned rows, or this migration will fail.
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_equip_fk"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE "uSkateConfig"
        ADD CONSTRAINT fk_uskateconfig_uskateruuid
        FOREIGN KEY ("uSkaterUUID") REFERENCES "uSkaterConfig"("uSkaterUUID") ON DELETE CASCADE
    """)
    op.execute("""
        ALTER TABLE "uSkaterBlades"
        ADD CONSTRAINT fk_uskaterblades_uskateruuid
        FOREIGN KEY ("uSkaterUUID") REFERENCES "uSkaterConfig"("uSkaterUUID") ON DELETE CASCADE
    """)
    op.execute("""
        ALTER TABLE "uSkaterBoots"
        ADD CONSTRAINT fk_uskaterboots_uskateruuid
        FOREIGN KEY ("uSkaterUUID") REFERENCES "uSkaterConfig"("uSkaterUUID") ON DELETE CASCADE
    """)


def downgrade() -> None:
    op.execute('ALTER TABLE "uSkateConfig"   DROP CONSTRAINT IF EXISTS fk_uskateconfig_uskateruuid')
    op.execute('ALTER TABLE "uSkaterBlades" DROP CONSTRAINT IF EXISTS fk_uskaterblades_uskateruuid')
    op.execute('ALTER TABLE "uSkaterBoots"   DROP CONSTRAINT IF EXISTS fk_uskaterboots_uskateruuid')
