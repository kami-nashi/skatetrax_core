"""Single-record detail views with child data.

Each class returns a structured dict for one parent record with all its
children -- ready to render as a detail page or serialize to JSON.

Pattern:  ClassName.get(record_id, uSkaterUUID, session=None) -> dict | None
"""
from ..cyberconnect2 import create_session
from ..t_locations import Locations
from ..t_coaches import Coaches
from ..t_memberships import Club_Directory


class EventDetail:
    """Full detail for a single competition / showcase / exhibition."""

    @staticmethod
    def get(event_id, uSkaterUUID, session=None):
        """Return a dict with parent event, joined location/coach, and all entries with scores.

        Returns None if the event doesn't exist or doesn't belong to the skater.
        """
        from ..t_events import (SkaterEvent, EventEntry, EventType, GoverningBody,
                                Score6_0, ScoreCJS, ScoreIJSComponent,
                                ScoreIJSElement, EventDeduction, EventCost)

        def _run(s):
            row = (
                s.query(
                    SkaterEvent,
                    Locations.rink_name,
                    Locations.rink_city,
                    Locations.rink_state,
                    Coaches.coach_Fname,
                    Coaches.coach_Lname,
                    Club_Directory.club_name,
                )
                .outerjoin(Locations, SkaterEvent.event_location == Locations.rink_id)
                .outerjoin(Coaches, SkaterEvent.coach_id == Coaches.coach_id)
                .outerjoin(Club_Directory, SkaterEvent.hosting_club == Club_Directory.club_id)
                .filter(
                    SkaterEvent.id == event_id,
                    SkaterEvent.uSkaterUUID == uSkaterUUID,
                )
                .first()
            )
            if not row:
                return None

            event = row[0]

            location = None
            if row.rink_name:
                location = {
                    "name": row.rink_name,
                    "city": row.rink_city,
                    "state": row.rink_state,
                }

            coach = None
            if row.coach_Fname or row.coach_Lname:
                coach = f"{row.coach_Fname or ''} {row.coach_Lname or ''}".strip()

            cost_rows = (
                s.query(EventCost)
                .filter(EventCost.event_id == event.id)
                .all()
            )
            costs = [
                {
                    "category": c.category,
                    "note": c.note,
                    "amount": c.amount,
                    "quantity": c.quantity,
                    "line_total": round(c.amount * c.quantity, 2),
                }
                for c in cost_rows
            ]
            event_cost = round(sum(c["line_total"] for c in costs), 2)

            entries_raw = (
                s.query(EventEntry, EventType, GoverningBody)
                .outerjoin(EventType, EventEntry.event_type == EventType.id)
                .outerjoin(GoverningBody, EventType.governing_body_id == GoverningBody.id)
                .filter(EventEntry.event_id == event.id)
                .all()
            )

            entries = []
            for entry, etype, gbody in entries_raw:
                scoring_system = etype.scoring_system if etype else None

                entry_dict = {
                    "id": str(entry.id),
                    "entry_date": str(entry.entry_date) if entry.entry_date else None,
                    "event_segment": entry.event_segment,
                    "event_level": entry.event_level,
                    "status": entry.status,
                    "placement": entry.placement,
                    "field_size": entry.field_size,
                    "majority": entry.majority,
                    "total_segment_score": entry.total_segment_score,
                    "source_url": entry.source_url,
                    "video_url": entry.video_url,
                    "event_results": entry.event_results,
                    "event_type": {
                        "category": etype.category,
                        "scoring_system": scoring_system,
                        "governing_body": gbody.short_name if gbody else None,
                    } if etype else None,
                    "scores": [],
                    "elements": [],
                    "deductions": [],
                }

                if scoring_system == "6.0":
                    rows = (
                        s.query(Score6_0)
                        .filter(Score6_0.entry_id == entry.id)
                        .order_by(Score6_0.judge_number)
                        .all()
                    )
                    entry_dict["scores"] = [
                        {
                            "judge_number": sc.judge_number,
                            "ordinal": sc.ordinal,
                            "technical_merit": sc.technical_merit,
                            "presentation": sc.presentation,
                        }
                        for sc in rows
                    ]

                elif scoring_system == "CJS":
                    rows = (
                        s.query(ScoreCJS)
                        .filter(ScoreCJS.entry_id == entry.id)
                        .order_by(ScoreCJS.judge_number)
                        .all()
                    )
                    entry_dict["scores"] = [
                        {
                            "judge_number": sc.judge_number,
                            "artistic_appeal": sc.artistic_appeal,
                            "performance": sc.performance,
                            "skating_skills": sc.skating_skills,
                        }
                        for sc in rows
                    ]

                elif scoring_system == "IJS":
                    comp_rows = (
                        s.query(ScoreIJSComponent)
                        .filter(ScoreIJSComponent.entry_id == entry.id)
                        .order_by(ScoreIJSComponent.judge_number)
                        .all()
                    )
                    entry_dict["scores"] = [
                        {
                            "judge_number": sc.judge_number,
                            "composition": sc.composition,
                            "presentation": sc.presentation,
                            "skating_skills": sc.skating_skills,
                        }
                        for sc in comp_rows
                    ]
                    elem_rows = (
                        s.query(ScoreIJSElement)
                        .filter(ScoreIJSElement.entry_id == entry.id)
                        .order_by(ScoreIJSElement.element_number)
                        .all()
                    )
                    entry_dict["elements"] = [
                        {
                            "element_number": el.element_number,
                            "element_name": el.element_name,
                            "base_value": el.base_value,
                            "goe": el.goe,
                            "final_score": el.final_score,
                        }
                        for el in elem_rows
                    ]

                deductions = (
                    s.query(EventDeduction)
                    .filter(EventDeduction.entry_id == entry.id)
                    .all()
                )
                entry_dict["deductions"] = [
                    {
                        "deduction_type": d.deduction_type,
                        "value": d.value,
                        "notes": d.notes,
                    }
                    for d in deductions
                ]

                entries.append(entry_dict)

            return {
                "id": str(event.id),
                "event_label": event.event_label,
                "event_date": event.event_date.isoformat() if event.event_date else None,
                "event_cost": event_cost,
                "costs": costs,
                "hosting_club": row.club_name,
                "location": location,
                "coach": coach,
                "notes": event.notes,
                "entries": entries,
            }

        if session is not None:
            return _run(session)
        else:
            with create_session() as s:
                return _run(s)
