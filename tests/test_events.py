"""Tests for the competition/event data layer.

Covers:
  - Event_Data.add_event_with_entries (all scoring systems + deductions)
  - Event_Data.add_entry (attach to existing event)
  - Event_Data.resolve_event_type
  - EventHistory.list_events / get_event_detail
  - EventDetail.get (6.0, CJS, IJS branches + deductions)
  - EventsTable.list_competitions (DataFrame)
  - SkaterAggregates: competition_cost, event_count, entry_count, podium_count
"""
import pytest
from datetime import date, datetime, timedelta
from uuid import uuid4

from skatetrax.models.ops.pencil import Event_Data
from skatetrax.models.ops.data_aggregates import SkaterAggregates, EventHistory
from skatetrax.models.ops.data_details import EventDetail
from skatetrax.models.t_events import (
    SkaterEvent, EventEntry, EventCost, Score6_0, ScoreCJS,
    ScoreIJSComponent, ScoreIJSElement, EventDeduction,
)

from tests.conftest import (
    NEW_USER_UUID, NEW_CONFIG_UUID,
    GOVERNING_BODY_USFSA_UUID, GOVERNING_BODY_NONE_UUID,
    EVENT_TYPE_COMP_6_0_USFSA_UUID, EVENT_TYPE_SHOWCASE_CJS_USFSA_UUID,
    EVENT_TYPE_COMP_IJS_USFSA_UUID, EVENT_TYPE_COMP_6_0_NONE_UUID,
    TEST_RINK_UUID, TEST_COACH_UUID, TEST_CLUB_UUID,
)

# run via: PYTHONPATH=. pytest tests/test_events.py -v


# ---------------------------------------------------------------------------
# Event_Data.add_event_with_entries
# ---------------------------------------------------------------------------
class TestAddEventWithEntries:

    def test_creates_event_and_entry(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Test Comp",
                "event_date": date(2026, 3, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[
                {
                    "event_segment": "Free Skate",
                    "event_level": "Adult High Beginner",
                    "placement": 1,
                    "field_size": 3,
                },
            ],
            costs_list=[
                {"category": "Competition Entry", "amount": 100.0},
            ],
            session=seeded_session,
        )
        assert event.event_label == "Test Comp"
        assert event.event_cost == 100.0
        entries = seeded_session.query(EventEntry).filter(
            EventEntry.event_id == event.id
        ).all()
        assert len(entries) == 1
        assert entries[0].placement == 1

    def test_multiple_entries(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Multi-Entry Comp",
                "event_date": date(2026, 3, 5),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[
                {"event_segment": "Short Program", "placement": 2, "field_size": 5},
                {"event_segment": "Free Skate", "placement": 3, "field_size": 5},
            ],
            session=seeded_session,
        )
        count = seeded_session.query(EventEntry).filter(
            EventEntry.event_id == event.id
        ).count()
        assert count == 2

    def test_with_6_0_scores(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "6.0 Comp",
                "event_date": date(2026, 3, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{"event_segment": "Free Skate"}],
            scores_by_entry={
                0: [
                    {"scoring_system": "6.0", "judge_number": 1, "ordinal": 1.0},
                    {"scoring_system": "6.0", "judge_number": 2, "ordinal": 2.0},
                    {"scoring_system": "6.0", "judge_number": 3, "ordinal": 1.0},
                ]
            },
            session=seeded_session,
        )
        entry = seeded_session.query(EventEntry).filter(
            EventEntry.event_id == event.id
        ).first()
        scores = seeded_session.query(Score6_0).filter(
            Score6_0.entry_id == entry.id
        ).all()
        assert len(scores) == 3
        assert scores[0].ordinal == 1.0

    def test_with_cjs_scores(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "CJS Showcase",
                "event_date": date(2026, 3, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{"event_segment": "Emotional Showcase"}],
            scores_by_entry={
                0: [
                    {
                        "scoring_system": "CJS",
                        "judge_number": 0,
                        "artistic_appeal": 4.5,
                        "performance": 5.0,
                        "skating_skills": 4.0,
                    }
                ]
            },
            session=seeded_session,
        )
        entry = seeded_session.query(EventEntry).filter(
            EventEntry.event_id == event.id
        ).first()
        scores = seeded_session.query(ScoreCJS).filter(
            ScoreCJS.entry_id == entry.id
        ).all()
        assert len(scores) == 1
        assert scores[0].artistic_appeal == 4.5
        assert scores[0].performance == 5.0

    def test_with_ijs_scores(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "IJS Comp",
                "event_date": date(2026, 3, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{"event_segment": "Free Skate"}],
            scores_by_entry={
                0: [
                    {
                        "scoring_system": "IJS_component",
                        "judge_number": 0,
                        "composition": 3.5,
                        "presentation": 4.0,
                        "skating_skills": 3.75,
                    },
                    {
                        "scoring_system": "IJS_element",
                        "element_number": 1,
                        "element_name": "1A",
                        "base_value": 1.1,
                        "goe": 0.1,
                        "final_score": 1.2,
                    },
                    {
                        "scoring_system": "IJS_element",
                        "element_number": 2,
                        "element_name": "2S",
                        "base_value": 1.3,
                        "goe": -0.2,
                        "final_score": 1.1,
                    },
                ]
            },
            session=seeded_session,
        )
        entry = seeded_session.query(EventEntry).filter(
            EventEntry.event_id == event.id
        ).first()
        comps = seeded_session.query(ScoreIJSComponent).filter(
            ScoreIJSComponent.entry_id == entry.id
        ).all()
        elems = seeded_session.query(ScoreIJSElement).filter(
            ScoreIJSElement.entry_id == entry.id
        ).all()
        assert len(comps) == 1
        assert comps[0].skating_skills == 3.75
        assert len(elems) == 2
        assert elems[0].element_name == "1A"

    def test_with_deductions(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Deduction Comp",
                "event_date": date(2026, 3, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{"event_segment": "Free Skate"}],
            deductions_by_entry={
                0: [
                    {"deduction_type": "Falls", "value": 1.0},
                    {"deduction_type": "Time violation", "value": 0.5},
                ]
            },
            session=seeded_session,
        )
        entry = seeded_session.query(EventEntry).filter(
            EventEntry.event_id == event.id
        ).first()
        deds = seeded_session.query(EventDeduction).filter(
            EventDeduction.entry_id == entry.id
        ).all()
        assert len(deds) == 2
        assert {d.deduction_type for d in deds} == {"Falls", "Time violation"}

    def test_unknown_scoring_system_raises(self, seeded_session):
        with pytest.raises(ValueError, match="Unknown scoring_system"):
            Event_Data.add_event_with_entries(
                event_dict={
                    "event_label": "Bad Comp",
                    "event_date": date(2026, 3, 1),
                    "uSkaterUUID": NEW_USER_UUID,
                },
                entries_list=[{"event_segment": "Free Skate"}],
                scores_by_entry={
                    0: [{"scoring_system": "INVALID", "judge_number": 1}]
                },
                session=seeded_session,
            )


# ---------------------------------------------------------------------------
# Event_Data.add_entry (to existing event)
# ---------------------------------------------------------------------------
class TestAddEntry:

    def _create_event(self, session):
        event = SkaterEvent(
            event_label="Existing Event",
            event_date=date(2026, 4, 1),
            uSkaterUUID=NEW_USER_UUID,
        )
        session.add(event)
        session.flush()
        return event

    def test_adds_entry_to_existing_event(self, seeded_session):
        event = self._create_event(seeded_session)
        entry = Event_Data.add_entry(
            event_id=event.id,
            entry_dict={
                "event_segment": "Short Program",
                "event_level": "Adult Bronze",
                "placement": 1,
                "field_size": 4,
                "uSkaterUUID": NEW_USER_UUID,
            },
            session=seeded_session,
        )
        assert entry.event_id == event.id
        assert entry.event_level == "Adult Bronze"

    def test_add_entry_with_scores_and_deductions(self, seeded_session):
        event = self._create_event(seeded_session)
        entry = Event_Data.add_entry(
            event_id=event.id,
            entry_dict={
                "event_segment": "Free Skate",
                "uSkaterUUID": NEW_USER_UUID,
            },
            scores=[
                {"scoring_system": "6.0", "judge_number": 1, "ordinal": 2.0},
            ],
            deductions=[
                {"deduction_type": "Falls", "value": 0.5},
            ],
            session=seeded_session,
        )
        scores = seeded_session.query(Score6_0).filter(
            Score6_0.entry_id == entry.id
        ).all()
        deds = seeded_session.query(EventDeduction).filter(
            EventDeduction.entry_id == entry.id
        ).all()
        assert len(scores) == 1
        assert len(deds) == 1

    def test_add_entry_nonexistent_event_raises(self, seeded_session):
        with pytest.raises(ValueError, match="not found"):
            Event_Data.add_entry(
                event_id=uuid4(),
                entry_dict={
                    "event_segment": "Ghost",
                    "uSkaterUUID": NEW_USER_UUID,
                },
                session=seeded_session,
            )


# ---------------------------------------------------------------------------
# Event_Data.resolve_event_type
# ---------------------------------------------------------------------------
class TestResolveEventType:

    def test_finds_usfsa_6_0(self, seeded_session):
        result = Event_Data.resolve_event_type(
            "Competition", "6.0", "USFSA", session=seeded_session
        )
        assert result == EVENT_TYPE_COMP_6_0_USFSA_UUID

    def test_finds_usfsa_cjs(self, seeded_session):
        result = Event_Data.resolve_event_type(
            "Showcase", "CJS", "USFSA", session=seeded_session
        )
        assert result == EVENT_TYPE_SHOWCASE_CJS_USFSA_UUID

    def test_finds_usfsa_ijs(self, seeded_session):
        result = Event_Data.resolve_event_type(
            "Competition", "IJS", "USFSA", session=seeded_session
        )
        assert result == EVENT_TYPE_COMP_IJS_USFSA_UUID

    def test_auto_creates_for_novel_combo(self, seeded_session):
        """A novel category+scoring+governing_body combo auto-creates the EventType."""
        from skatetrax.models.t_events import EventType
        result = Event_Data.resolve_event_type(
            "Unknown", "6.0", "USFSA", session=seeded_session
        )
        assert result is not None
        et = seeded_session.query(EventType).filter_by(id=result).first()
        assert et.category == "Unknown"
        assert et.scoring_system == "6.0"

    def test_auto_creates_exhibition_no_scoring(self, seeded_session):
        """Exhibition with no scoring system or governing body auto-creates an EventType."""
        from skatetrax.models.t_events import EventType
        result = Event_Data.resolve_event_type(
            "Exhibition", None, None, session=seeded_session
        )
        assert result is not None
        et = seeded_session.query(EventType).filter_by(id=result).first()
        assert et.category == "Exhibition"
        assert et.scoring_system is None
        assert et.governing_body_id is None

    def test_auto_create_is_idempotent(self, seeded_session):
        """Calling resolve twice for the same combo returns the same UUID."""
        first = Event_Data.resolve_event_type(
            "Exhibition", None, None, session=seeded_session
        )
        second = Event_Data.resolve_event_type(
            "Exhibition", None, None, session=seeded_session
        )
        assert first == second

    def test_auto_creates_with_scoring_system(self, seeded_session):
        """Auto-creates a new EventType when category+scoring+body combo is novel."""
        from skatetrax.models.t_events import EventType
        result = Event_Data.resolve_event_type(
            "Showcase", "6.0", "USFSA", session=seeded_session
        )
        assert result is not None
        et = seeded_session.query(EventType).filter_by(id=result).first()
        assert et.category == "Showcase"
        assert et.scoring_system == "6.0"


# ---------------------------------------------------------------------------
# EventHistory.list_events / get_event_detail
# ---------------------------------------------------------------------------
class TestEventHistory:

    def _seed_events(self, session):
        e1 = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "First Comp",
                "event_date": date(2026, 1, 15),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[
                {"event_segment": "Short Program", "placement": 1, "field_size": 3},
            ],
            costs_list=[
                {"category": "Competition Entry", "amount": 50.0},
            ],
            session=session,
        )
        e2 = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Second Comp",
                "event_date": date(2026, 2, 20),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[
                {"event_segment": "Free Skate A", "placement": 2, "field_size": 4},
                {"event_segment": "Free Skate B", "placement": 3, "field_size": 5},
            ],
            costs_list=[
                {"category": "Competition Entry", "amount": 75.0},
            ],
            session=session,
        )
        return e1, e2

    def test_list_events_returns_all(self, seeded_session):
        self._seed_events(seeded_session)
        eh = EventHistory(NEW_USER_UUID, session=seeded_session)
        events = eh.list_events()
        assert len(events) == 2

    def test_list_events_ordered_desc(self, seeded_session):
        self._seed_events(seeded_session)
        eh = EventHistory(NEW_USER_UUID, session=seeded_session)
        events = eh.list_events()
        assert events[0]["event_label"] == "Second Comp"
        assert events[1]["event_label"] == "First Comp"

    def test_list_events_entry_counts(self, seeded_session):
        self._seed_events(seeded_session)
        eh = EventHistory(NEW_USER_UUID, session=seeded_session)
        events = eh.list_events()
        counts = {e["event_label"]: e["entry_count"] for e in events}
        assert counts["First Comp"] == 1
        assert counts["Second Comp"] == 2

    def test_empty_for_unknown_user(self, seeded_session):
        eh = EventHistory(uuid4(), session=seeded_session)
        assert eh.list_events() == []


# ---------------------------------------------------------------------------
# EventDetail.get -- all scoring branches
# ---------------------------------------------------------------------------
class TestEventDetail:

    def test_returns_none_for_missing_event(self, seeded_session):
        result = EventDetail.get(uuid4(), NEW_USER_UUID, session=seeded_session)
        assert result is None

    def test_returns_none_for_wrong_skater(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Someone Else's",
                "event_date": date(2026, 3, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{"event_segment": "FS"}],
            session=seeded_session,
        )
        result = EventDetail.get(event.id, uuid4(), session=seeded_session)
        assert result is None

    def test_basic_event_fields(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Detail Test",
                "event_date": date(2026, 3, 10),
                "hosting_club": TEST_CLUB_UUID,
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[
                {"event_segment": "Free Skate", "placement": 2, "field_size": 6},
            ],
            costs_list=[
                {"category": "Competition Entry", "amount": 150.0},
                {"category": "Practice Ice", "amount": 25.0, "quantity": 2},
            ],
            session=seeded_session,
        )
        detail = EventDetail.get(event.id, NEW_USER_UUID, session=seeded_session)
        assert detail["event_label"] == "Detail Test"
        assert detail["event_cost"] == 200.0
        assert detail["hosting_club"] == "Test FSC"
        assert len(detail["costs"]) == 2
        assert len(detail["entries"]) == 1
        assert detail["entries"][0]["placement"] == 2

    def test_6_0_scores_in_detail(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Detail 6.0",
                "event_date": date(2026, 3, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{
                "event_segment": "Free Skate",
                "event_type": EVENT_TYPE_COMP_6_0_USFSA_UUID,
            }],
            scores_by_entry={
                0: [
                    {"scoring_system": "6.0", "judge_number": 1, "ordinal": 1.0,
                     "technical_merit": 3.5, "presentation": 3.8},
                    {"scoring_system": "6.0", "judge_number": 2, "ordinal": 2.0,
                     "technical_merit": 3.3, "presentation": 3.6},
                ]
            },
            session=seeded_session,
        )
        detail = EventDetail.get(event.id, NEW_USER_UUID, session=seeded_session)
        entry = detail["entries"][0]
        assert entry["event_type"]["scoring_system"] == "6.0"
        assert entry["event_type"]["governing_body"] == "USFSA"
        assert len(entry["scores"]) == 2
        assert entry["scores"][0]["technical_merit"] == 3.5

    def test_cjs_scores_in_detail(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Detail CJS",
                "event_date": date(2026, 3, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{
                "event_segment": "Emotional Showcase",
                "event_type": EVENT_TYPE_SHOWCASE_CJS_USFSA_UUID,
            }],
            scores_by_entry={
                0: [
                    {
                        "scoring_system": "CJS",
                        "judge_number": 0,
                        "artistic_appeal": 5.5,
                        "performance": 5.0,
                        "skating_skills": 4.75,
                    },
                ]
            },
            session=seeded_session,
        )
        detail = EventDetail.get(event.id, NEW_USER_UUID, session=seeded_session)
        entry = detail["entries"][0]
        assert entry["event_type"]["scoring_system"] == "CJS"
        assert len(entry["scores"]) == 1
        assert entry["scores"][0]["artistic_appeal"] == 5.5
        assert entry["scores"][0]["performance"] == 5.0

    def test_ijs_scores_in_detail(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Detail IJS",
                "event_date": date(2026, 3, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{
                "event_segment": "Free Skate",
                "event_type": EVENT_TYPE_COMP_IJS_USFSA_UUID,
            }],
            scores_by_entry={
                0: [
                    {
                        "scoring_system": "IJS_component",
                        "judge_number": 0,
                        "composition": 4.0,
                        "presentation": 3.5,
                        "skating_skills": 4.25,
                    },
                    {
                        "scoring_system": "IJS_element",
                        "element_number": 1,
                        "element_name": "1A",
                        "base_value": 1.1,
                        "goe": 0.15,
                        "final_score": 1.25,
                    },
                ]
            },
            session=seeded_session,
        )
        detail = EventDetail.get(event.id, NEW_USER_UUID, session=seeded_session)
        entry = detail["entries"][0]
        assert entry["event_type"]["scoring_system"] == "IJS"
        assert len(entry["scores"]) == 1
        assert entry["scores"][0]["skating_skills"] == 4.25
        assert len(entry["elements"]) == 1
        assert entry["elements"][0]["element_name"] == "1A"

    def test_deductions_in_detail(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Detail Deductions",
                "event_date": date(2026, 3, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{"event_segment": "Free Skate"}],
            deductions_by_entry={
                0: [{"deduction_type": "Falls", "value": 1.0, "notes": "2 falls"}]
            },
            session=seeded_session,
        )
        detail = EventDetail.get(event.id, NEW_USER_UUID, session=seeded_session)
        deds = detail["entries"][0]["deductions"]
        assert len(deds) == 1
        assert deds[0]["deduction_type"] == "Falls"
        assert deds[0]["value"] == 1.0
        assert deds[0]["notes"] == "2 falls"


# ---------------------------------------------------------------------------
# EventsTable.list_competitions (DataFrame)
# ---------------------------------------------------------------------------
class TestEventsTable:

    def test_returns_dataframe(self, seeded_session):
        from skatetrax.models.ops.data_tables import EventsTable
        Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "DF Comp",
                "event_date": date(2026, 3, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[
                {"event_segment": "Free Skate", "event_level": "Adult Bronze",
                 "placement": 1, "field_size": 3},
            ],
            costs_list=[
                {"category": "Competition Entry", "amount": 120.0},
            ],
            session=seeded_session,
        )
        df = EventsTable.list_competitions(
            NEW_USER_UUID, session=seeded_session
        )
        assert len(df) == 1
        assert df.iloc[0]["event_label"] == "DF Comp"
        assert df.iloc[0]["placement"] == 1
        assert df.iloc[0]["event_cost"] == 120.0
        assert "entry_date" in df.columns
        assert "event_id" in df.columns
        assert "video_url" in df.columns
        assert "location_name" in df.columns
        assert "location_city" in df.columns
        assert "location_state" in df.columns

    def test_empty_for_no_events(self, seeded_session):
        from skatetrax.models.ops.data_tables import EventsTable
        df = EventsTable.list_competitions(
            uuid4(), session=seeded_session
        )
        assert len(df) == 0

    def test_category_filter(self, seeded_session):
        from skatetrax.models.ops.data_tables import EventsTable
        Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Comp Event",
                "event_date": date(2026, 3, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{
                "event_segment": "Free Skate",
                "event_type": EVENT_TYPE_COMP_6_0_USFSA_UUID,
            }],
            session=seeded_session,
        )
        Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Showcase Event",
                "event_date": date(2026, 3, 2),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{
                "event_segment": "Emotional",
                "event_type": EVENT_TYPE_SHOWCASE_CJS_USFSA_UUID,
            }],
            session=seeded_session,
        )
        comp_df = EventsTable.list_competitions(
            NEW_USER_UUID, category="Competition", session=seeded_session
        )
        assert len(comp_df) == 1
        assert comp_df.iloc[0]["event_label"] == "Comp Event"

        showcase_df = EventsTable.list_competitions(
            NEW_USER_UUID, category="Showcase", session=seeded_session
        )
        assert len(showcase_df) == 1
        assert showcase_df.iloc[0]["event_label"] == "Showcase Event"

        all_df = EventsTable.list_competitions(
            NEW_USER_UUID, session=seeded_session
        )
        assert len(all_df) == 2

    def test_exhibition_category_filter(self, seeded_session):
        from skatetrax.models.ops.data_tables import EventsTable
        et_id = Event_Data.resolve_event_type(
            "Exhibition", None, None, session=seeded_session
        )
        Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Holiday Show",
                "event_date": date(2026, 12, 14),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{
                "event_segment": "Adult Class Program",
                "event_type": et_id,
                "status": "Performed",
                "video_url": "https://youtu.be/example",
            }],
            session=seeded_session,
        )
        df = EventsTable.list_competitions(
            NEW_USER_UUID, category="Exhibition", session=seeded_session
        )
        assert len(df) == 1
        assert df.iloc[0]["event_label"] == "Holiday Show"
        assert df.iloc[0]["video_url"] == "https://youtu.be/example"
        assert df.iloc[0]["status"] == "Performed"


# ---------------------------------------------------------------------------
# SkaterAggregates: competition metrics
# ---------------------------------------------------------------------------
class TestCompetitionAggregates:

    def _seed_comp_data(self, session):
        """Create 2 events: one recent, one old. 3 entries total, 2 podium."""
        Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Recent Comp",
                "event_date": date.today() - timedelta(days=10),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[
                {"event_segment": "Short Program", "placement": 1, "field_size": 5},
                {"event_segment": "Free Skate", "placement": 4, "field_size": 5},
            ],
            costs_list=[
                {"category": "Competition Entry", "amount": 100.0},
            ],
            session=session,
        )
        Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Old Comp",
                "event_date": date.today() - timedelta(days=90),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[
                {"event_segment": "Free Skate", "placement": 2, "field_size": 4},
            ],
            costs_list=[
                {"category": "Competition Entry", "amount": 75.0},
            ],
            session=session,
        )

    def test_competition_cost_total(self, seeded_session):
        self._seed_comp_data(seeded_session)
        sa = SkaterAggregates(NEW_USER_UUID, session=seeded_session)
        assert sa.competition_cost() == "175.00"

    def test_competition_cost_30d(self, seeded_session):
        self._seed_comp_data(seeded_session)
        sa = SkaterAggregates(NEW_USER_UUID, session=seeded_session)
        assert sa.competition_cost("30d") == "100.00"

    def test_event_count_total(self, seeded_session):
        self._seed_comp_data(seeded_session)
        sa = SkaterAggregates(NEW_USER_UUID, session=seeded_session)
        assert sa.event_count() == 2

    def test_event_count_30d(self, seeded_session):
        self._seed_comp_data(seeded_session)
        sa = SkaterAggregates(NEW_USER_UUID, session=seeded_session)
        assert sa.event_count("30d") == 1

    def test_entry_count_total(self, seeded_session):
        self._seed_comp_data(seeded_session)
        sa = SkaterAggregates(NEW_USER_UUID, session=seeded_session)
        assert sa.entry_count() == 3

    def test_entry_count_30d(self, seeded_session):
        self._seed_comp_data(seeded_session)
        sa = SkaterAggregates(NEW_USER_UUID, session=seeded_session)
        assert sa.entry_count("30d") == 2

    def test_podium_count_total(self, seeded_session):
        self._seed_comp_data(seeded_session)
        sa = SkaterAggregates(NEW_USER_UUID, session=seeded_session)
        assert sa.podium_count() == 2

    def test_podium_count_30d(self, seeded_session):
        self._seed_comp_data(seeded_session)
        sa = SkaterAggregates(NEW_USER_UUID, session=seeded_session)
        assert sa.podium_count("30d") == 1

    def test_all_zeros_for_new_user(self, seeded_session):
        sa = SkaterAggregates(uuid4(), session=seeded_session)
        assert sa.competition_cost() == "0.00"
        assert sa.event_count() == 0
        assert sa.entry_count() == 0
        assert sa.podium_count() == 0


# ---------------------------------------------------------------------------
# EventEntry.status
# ---------------------------------------------------------------------------
class TestEntryStatus:

    def test_default_status_is_committed(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Status Default Comp",
                "event_date": date(2026, 7, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[
                {"event_segment": "Free Skate", "event_level": "Adult Bronze"},
            ],
            session=seeded_session,
        )
        entry = seeded_session.query(EventEntry).filter(
            EventEntry.event_id == event.id
        ).first()
        assert entry.status == "Committed"

    def test_explicit_status_withdrew(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Withdrew Comp",
                "event_date": date(2026, 8, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[
                {
                    "event_segment": "Showcase Emotional",
                    "event_level": "Adult High Beginner",
                    "status": "Withdrew",
                },
            ],
            session=seeded_session,
        )
        entry = seeded_session.query(EventEntry).filter(
            EventEntry.event_id == event.id
        ).first()
        assert entry.status == "Withdrew"

    def test_explicit_status_scored(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Scored Comp",
                "event_date": date(2026, 3, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[
                {
                    "event_segment": "Free Skate",
                    "event_level": "Adult Gold",
                    "placement": 2,
                    "field_size": 5,
                    "status": "Scored",
                },
            ],
            session=seeded_session,
        )
        entry = seeded_session.query(EventEntry).filter(
            EventEntry.event_id == event.id
        ).first()
        assert entry.status == "Scored"

    def test_add_entry_with_status(self, seeded_session):
        event = SkaterEvent(
            event_label="Mixed Status Event",
            event_date=date(2026, 6, 15),
            uSkaterUUID=NEW_USER_UUID,
        )
        seeded_session.add(event)
        seeded_session.flush()

        entry = Event_Data.add_entry(
            event_id=event.id,
            entry_dict={
                "event_segment": "Adult Singles",
                "status": "Committed",
                "uSkaterUUID": NEW_USER_UUID,
            },
            session=seeded_session,
        )
        assert entry.status == "Committed"

        entry2 = Event_Data.add_entry(
            event_id=event.id,
            entry_dict={
                "event_segment": "Showcase Emotional",
                "status": "Withdrew",
                "uSkaterUUID": NEW_USER_UUID,
            },
            session=seeded_session,
        )
        assert entry2.status == "Withdrew"

    def test_status_in_detail_view(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Detail Status Comp",
                "event_date": date(2026, 5, 10),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[
                {"event_segment": "Free Skate", "status": "Scored"},
                {"event_segment": "Showcase", "status": "Withdrew"},
            ],
            session=seeded_session,
        )
        detail = EventDetail.get(event.id, NEW_USER_UUID, session=seeded_session)
        statuses = {e["event_segment"]: e["status"] for e in detail["entries"]}
        assert statuses["Free Skate"] == "Scored"
        assert statuses["Showcase"] == "Withdrew"

    def test_status_in_list_competitions(self, seeded_session):
        from skatetrax.models.ops.data_tables import EventsTable
        Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "List Status Comp",
                "event_date": date(2026, 9, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[
                {"event_segment": "Free Skate", "status": "Committed"},
            ],
            session=seeded_session,
        )
        df = EventsTable.list_competitions(NEW_USER_UUID, session=seeded_session)
        match = df[df["event_label"] == "List Status Comp"]
        assert len(match) == 1
        assert match.iloc[0]["status"] == "Committed"


# ---------------------------------------------------------------------------
# EventCost line items
# ---------------------------------------------------------------------------
class TestEventCosts:

    def test_event_cost_property_no_costs(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "No Cost Comp",
                "event_date": date(2026, 4, 1),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{"event_segment": "Free Skate"}],
            session=seeded_session,
        )
        assert event.event_cost == 0.0

    def test_event_cost_property_with_costs(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Costed Comp",
                "event_date": date(2026, 4, 2),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{"event_segment": "Free Skate"}],
            costs_list=[
                {"category": "Competition Entry", "amount": 155.0},
                {"category": "Practice Ice", "amount": 25.0, "quantity": 2},
                {"category": "Admin Fee", "amount": 15.0},
            ],
            session=seeded_session,
        )
        assert event.event_cost == 220.0

    def test_cost_note_stored(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Noted Comp",
                "event_date": date(2026, 4, 3),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{"event_segment": "Free Skate"}],
            costs_list=[
                {"category": "Competition Entry", "amount": 90.0,
                 "note": "IJS Singles - 2nd event"},
            ],
            session=seeded_session,
        )
        cost = seeded_session.query(EventCost).filter(
            EventCost.event_id == event.id
        ).first()
        assert cost.note == "IJS Singles - 2nd event"
        assert cost.category == "Competition Entry"

    def test_costs_in_detail_view(self, seeded_session):
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Detail Costs Comp",
                "event_date": date(2026, 4, 4),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{"event_segment": "Free Skate"}],
            costs_list=[
                {"category": "Competition Entry", "amount": 100.0},
                {"category": "Taxes", "amount": 8.50},
            ],
            session=seeded_session,
        )
        detail = EventDetail.get(event.id, NEW_USER_UUID, session=seeded_session)
        assert detail["event_cost"] == 108.50
        assert len(detail["costs"]) == 2
        categories = {c["category"] for c in detail["costs"]}
        assert categories == {"Competition Entry", "Taxes"}
        for c in detail["costs"]:
            assert "line_total" in c

    def test_multiple_categories(self, seeded_session):
        """Verify all cost categories can coexist on one event."""
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Multi-Cat Comp",
                "event_date": date(2026, 4, 5),
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{"event_segment": "Free Skate"}],
            costs_list=[
                {"category": "Competition Entry", "amount": 155.0},
                {"category": "Competition Entry", "amount": 90.0,
                 "note": "2nd event"},
                {"category": "Practice Ice", "amount": 25.0, "quantity": 2},
                {"category": "Admin Fee", "amount": 15.0},
                {"category": "Coach Fee", "amount": 100.0},
                {"category": "Taxes", "amount": 12.05},
            ],
            session=seeded_session,
        )
        costs = seeded_session.query(EventCost).filter(
            EventCost.event_id == event.id
        ).all()
        assert len(costs) == 6
        assert event.event_cost == 155.0 + 90.0 + 50.0 + 15.0 + 100.0 + 12.05

    def test_old_event_cost_kwarg_ignored(self, seeded_session):
        """Passing event_cost in event_dict should not break anything."""
        event = Event_Data.add_event_with_entries(
            event_dict={
                "event_label": "Legacy Kwarg Comp",
                "event_date": date(2026, 4, 6),
                "event_cost": 999.0,
                "uSkaterUUID": NEW_USER_UUID,
            },
            entries_list=[{"event_segment": "Free Skate"}],
            session=seeded_session,
        )
        assert event.event_cost == 0.0
