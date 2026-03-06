"""Rename ScoreCJS.composition to .performance

Revision ID: 010_rename_cjs_composition
Revises: 009_entry_date_column
Create Date: 2026-03-01

The CJS scoring system uses Artistic Appeal, Performance, and
Skating Skills -- not Composition.  Renames the column to match
the actual USFSA CJS terminology.
"""
from typing import Sequence, Union

from alembic import op

revision: str = '010_rename_cjs_composition'
down_revision: Union[str, None] = '009_entry_date_column'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('e_scores_cjs', 'composition', new_column_name='performance')


def downgrade() -> None:
    op.alter_column('e_scores_cjs', 'performance', new_column_name='composition')
