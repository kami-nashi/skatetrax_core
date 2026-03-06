"""Competition results schema

Revision ID: 007_competition_results_schema
Revises: 006_drop_legacy_roles
Create Date: 2026-03-04

Replaces the flat e_competition / e_competition_types tables with a
parent/child event structure, a dimensional event-type table, a
governing-bodies reference table, scoring tables for all three systems
(6.0, CJS, IJS), and deductions.

Also re-points e_tests.test_type FK from the dropped e_competition_types
to the new e_event_types table.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "007_competition_results_schema"
down_revision: Union[str, None] = "006_drop_legacy_roles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ── Seed data (deterministic UUIDs for reproducibility) ─────────────────

GOVERNING_BODIES = [
    ("a0000000-0000-0000-0000-000000000001", "None", "Unaffiliated"),
    ("a0000000-0000-0000-0000-000000000002", "USFSA", "U.S. Figure Skating Association"),
    ("a0000000-0000-0000-0000-000000000003", "ISI", "Ice Sports Industry"),
    ("a0000000-0000-0000-0000-000000000004", "Other", "Other"),
]

EVENT_TYPES = [
    ("b0000000-0000-0000-0000-000000000001", "Competition", "6.0",  "a0000000-0000-0000-0000-000000000002", False),
    ("b0000000-0000-0000-0000-000000000002", "Competition", "6.0",  "a0000000-0000-0000-0000-000000000001", False),
    ("b0000000-0000-0000-0000-000000000003", "Showcase",    "CJS",  "a0000000-0000-0000-0000-000000000002", False),
    ("b0000000-0000-0000-0000-000000000004", "Showcase",    None,   "a0000000-0000-0000-0000-000000000001", False),
    ("b0000000-0000-0000-0000-000000000005", "Exhibition",  None,   "a0000000-0000-0000-0000-000000000001", False),
    ("b0000000-0000-0000-0000-000000000006", "Competition", "IJS",  "a0000000-0000-0000-0000-000000000002", False),
]


def upgrade() -> None:
    # ── Drop legacy tables ──────────────────────────────────────────────
    # Remove FK on e_tests first so the referenced table can be dropped
    op.drop_constraint("e_tests_test_type_fkey", "e_tests", type_="foreignkey")
    op.drop_table("e_competition")
    op.drop_table("e_competition_types")

    # ── Create new tables ───────────────────────────────────────────────
    op.create_table(
        "e_governing_bodies",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("short_name", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
    )

    op.create_table(
        "e_event_types",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("scoring_system", sa.String(), nullable=True),
        sa.Column("governing_body_id", sa.UUID(),
                  sa.ForeignKey("e_governing_bodies.id"), nullable=True),
        sa.Column("single_mark", sa.Boolean(), server_default="false"),
    )

    op.create_table(
        "e_events",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("event_label", sa.String(), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("event_cost", sa.Float(), server_default="0"),
        sa.Column("event_location", sa.UUID(),
                  sa.ForeignKey("locations.rink_id", ondelete="SET NULL"),
                  nullable=True),
        sa.Column("hosting_club", sa.String(), nullable=True),
        sa.Column("coach_id", sa.UUID(),
                  sa.ForeignKey("coaches.coach_id", ondelete="SET NULL"),
                  nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("uSkaterUUID", sa.UUID(),
                  sa.ForeignKey("uSkaterConfig.uSkaterUUID", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("uSkaterConfig", sa.UUID(),
                  sa.ForeignKey("uSkateConfig.sConfigID", ondelete="SET NULL"),
                  nullable=True),
    )

    op.create_table(
        "e_event_entries",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("event_id", sa.UUID(),
                  sa.ForeignKey("e_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_segment", sa.String(), nullable=True),
        sa.Column("event_level", sa.String(), nullable=True),
        sa.Column("event_type", sa.UUID(),
                  sa.ForeignKey("e_event_types.id"), nullable=True),
        sa.Column("placement", sa.Integer(), nullable=True),
        sa.Column("field_size", sa.Integer(), nullable=True),
        sa.Column("majority", sa.String(), nullable=True),
        sa.Column("total_segment_score", sa.Float(), nullable=True),
        sa.Column("source_url", sa.String(), nullable=True),
        sa.Column("video_url", sa.String(), nullable=True),
        sa.Column("event_results", sa.String(), nullable=True),
        sa.Column("uSkaterUUID", sa.UUID(),
                  sa.ForeignKey("uSkaterConfig.uSkaterUUID", ondelete="CASCADE"),
                  nullable=False),
    )

    op.create_table(
        "e_scores_6_0",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("entry_id", sa.UUID(),
                  sa.ForeignKey("e_event_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("judge_number", sa.Integer(), nullable=False),
        sa.Column("ordinal", sa.Float(), nullable=True),
        sa.Column("technical_merit", sa.Float(), nullable=True),
        sa.Column("presentation", sa.Float(), nullable=True),
        sa.Column("uSkaterUUID", sa.UUID(),
                  sa.ForeignKey("uSkaterConfig.uSkaterUUID", ondelete="CASCADE"),
                  nullable=False),
    )

    op.create_table(
        "e_scores_cjs",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("entry_id", sa.UUID(),
                  sa.ForeignKey("e_event_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("judge_number", sa.Integer(), nullable=False),
        sa.Column("artistic_appeal", sa.Float(), nullable=True),
        sa.Column("composition", sa.Float(), nullable=True),
        sa.Column("skating_skills", sa.Float(), nullable=True),
        sa.Column("uSkaterUUID", sa.UUID(),
                  sa.ForeignKey("uSkaterConfig.uSkaterUUID", ondelete="CASCADE"),
                  nullable=False),
    )

    op.create_table(
        "e_scores_ijs_components",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("entry_id", sa.UUID(),
                  sa.ForeignKey("e_event_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("judge_number", sa.Integer(), nullable=False),
        sa.Column("composition", sa.Float(), nullable=True),
        sa.Column("presentation", sa.Float(), nullable=True),
        sa.Column("skating_skills", sa.Float(), nullable=True),
        sa.Column("uSkaterUUID", sa.UUID(),
                  sa.ForeignKey("uSkaterConfig.uSkaterUUID", ondelete="CASCADE"),
                  nullable=False),
    )

    op.create_table(
        "e_scores_ijs_elements",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("entry_id", sa.UUID(),
                  sa.ForeignKey("e_event_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("element_number", sa.Integer(), nullable=False),
        sa.Column("element_name", sa.String(), nullable=True),
        sa.Column("base_value", sa.Float(), nullable=True),
        sa.Column("goe", sa.Float(), nullable=True),
        sa.Column("final_score", sa.Float(), nullable=True),
        sa.Column("uSkaterUUID", sa.UUID(),
                  sa.ForeignKey("uSkaterConfig.uSkaterUUID", ondelete="CASCADE"),
                  nullable=False),
    )

    op.create_table(
        "e_deductions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("entry_id", sa.UUID(),
                  sa.ForeignKey("e_event_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("deduction_type", sa.String(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("uSkaterUUID", sa.UUID(),
                  sa.ForeignKey("uSkaterConfig.uSkaterUUID", ondelete="CASCADE"),
                  nullable=False),
    )

    # ── Re-point e_tests FK ─────────────────────────────────────────────
    op.create_foreign_key(
        "e_tests_test_type_fkey", "e_tests", "e_event_types",
        ["test_type"], ["id"], ondelete="CASCADE",
    )

    # ── Seed governing bodies and event types ───────────────────────────
    gb_table = sa.table(
        "e_governing_bodies",
        sa.column("id", sa.UUID),
        sa.column("short_name", sa.String),
        sa.column("full_name", sa.String),
    )
    op.bulk_insert(gb_table, [
        {"id": uid, "short_name": sn, "full_name": fn}
        for uid, sn, fn in GOVERNING_BODIES
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
    # Remove new FK on e_tests
    op.drop_constraint("e_tests_test_type_fkey", "e_tests", type_="foreignkey")

    # Drop new tables (children first)
    op.drop_table("e_deductions")
    op.drop_table("e_scores_ijs_elements")
    op.drop_table("e_scores_ijs_components")
    op.drop_table("e_scores_cjs")
    op.drop_table("e_scores_6_0")
    op.drop_table("e_event_entries")
    op.drop_table("e_events")
    op.drop_table("e_event_types")
    op.drop_table("e_governing_bodies")

    # Recreate legacy tables
    op.create_table(
        "e_competition_types",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("label", sa.String(), nullable=True),
        sa.Column("governing_body", sa.String(), nullable=True),
    )

    op.create_table(
        "e_competition",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("event_cost", sa.Float(), nullable=True),
        sa.Column("event_label", sa.String(), nullable=True),
        sa.Column("event_level", sa.String(), nullable=True),
        sa.Column("event_type", sa.UUID(),
                  sa.ForeignKey("e_competition_types.id", ondelete="CASCADE"),
                  nullable=True),
        sa.Column("event_results", sa.String(), nullable=True),
        sa.Column("event_date", sa.DateTime(), nullable=True),
        sa.Column("event_location", sa.UUID(),
                  sa.ForeignKey("locations.rink_id", ondelete="CASCADE"),
                  nullable=True),
        sa.Column("uSkaterUUID", sa.UUID(),
                  sa.ForeignKey("uSkaterConfig.uSkaterUUID", ondelete="CASCADE"),
                  nullable=True),
        sa.Column("uSkaterConfig", sa.UUID(),
                  sa.ForeignKey("uSkateConfig.sConfigID", ondelete="CASCADE"),
                  nullable=True),
    )

    # Restore original FK on e_tests
    op.create_foreign_key(
        "e_tests_test_type_fkey", "e_tests", "e_competition_types",
        ["test_type"], ["id"], ondelete="CASCADE",
    )
