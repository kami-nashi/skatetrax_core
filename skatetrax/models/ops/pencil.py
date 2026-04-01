from sqlalchemy import func
from datetime import datetime

from ..cyberconnect2 import create_session

from ..t_auth import uAuthTable

from ..t_ice_time import Ice_Time
from ..t_locations import Locations, Punch_cards
from ..t_maint import uSkaterMaint
from ..t_icetype import IceType
from ..t_coaches import Coaches
from ..t_equip import uSkateConfig, uSkaterBlades, uSkaterBoots
from ..t_classes import Skate_School
from ..t_memberships import Club_Directory, Club_Members
from ..t_events import (GoverningBody, EventType, SkaterEvent, EventEntry,
                        Score6_0, ScoreCJS, ScoreIJSComponent, ScoreIJSElement,
                        EventDeduction, EventCost)
from ..t_music import MusicTrack, MusicPlaylist, MusicPlaylistTrack

from ..t_skaterMeta import uSkaterConfig

class Coach_Data():

    def add_coaches(coaches, session=None):
        def _run(sess):
            for coach in coaches:
                try:
                    sess.add(Coaches(**coach))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)


class Equipment_Data():

    def add_blades(blades, session=None):
        def _run(sess):
            for blade in blades:
                try:
                    sess.add(uSkaterBlades(**blade))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_boots(boots, session=None):
        def _run(sess):
            for boot in boots:
                try:
                    sess.add(uSkaterBoots(**boot))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_combo(configs, session=None):
        def _run(sess):
            for config in configs:
                try:
                    sess.add(uSkateConfig(**config))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_maintenance(maint_sess, session=None):
        def _run(sess):
            for maint in maint_sess:
                try:
                    sess.add(uSkaterMaint(**maint))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)


class Ice_Session():

    def add_skate_time(sessions, session=None):
        def _run(sess):
            for asession in sessions:
                try:
                    sess.add(Ice_Time(**asession))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_skate_school(classes, session=None):
        def _run(sess):
            for aclass in classes:
                try:
                    sess.add(Skate_School(**aclass))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)


class Location_Data():

    def add_ice_type(types, session=None):
        def _run(sess):
            for ice_type in types:
                try:
                    sess.add(IceType(**ice_type))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_ice_rink(rinks, session=None):
        def _run(sess):
            for rink in rinks:
                try:
                    sess.add(Locations(**rink))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_punchcard(cards, session=None):
        def _run(sess):
            for card in cards:
                try:
                    sess.add(Punch_cards(**card))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)


class User_Data():

    def add_skater(skater_data, session=None):
        def _run(sess):
            for data in skater_data:
                try:
                    sess.add(uSkaterConfig(**data))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)



class Club_Data():

    def add_club(club_data, session=None):
        def _run(sess):
            for data in club_data:
                try:
                    sess.add(Club_Directory(**data))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_member(member_data, session=None):
        def _run(sess):
            for data in member_data:
                try:
                    sess.add(Club_Members(**data))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)
        
class Event_Data():

    def add_governing_bodies(bodies, session=None):
        def _run(sess):
            for body in bodies:
                try:
                    sess.add(GoverningBody(**body))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_event_types(types, session=None):
        def _run(sess):
            for etype in types:
                try:
                    sess.add(EventType(**etype))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def resolve_event_type(category, scoring_system=None, governing_body_short=None, session=None):
        """Look up an EventType UUID by category + optional scoring_system + governing body.

        When scoring_system and governing_body_short are both None (e.g. for
        exhibitions), matches on category alone.

        Args:
            category: e.g. "Competition", "Showcase", "Exhibition"
            scoring_system: e.g. "6.0", "CJS", "IJS", or None
            governing_body_short: e.g. "USFSA", "ISI", or None
            session: optional external SQLAlchemy session.
        Returns:
            UUID of the matching EventType, or None.
        """
        def _run(sess):
            q = (
                sess.query(EventType.id)
                .outerjoin(GoverningBody, EventType.governing_body_id == GoverningBody.id)
                .filter(EventType.category == category)
            )
            if scoring_system is not None:
                q = q.filter(EventType.scoring_system == scoring_system)
            else:
                q = q.filter(EventType.scoring_system.is_(None))
            if governing_body_short is not None:
                q = q.filter(GoverningBody.short_name == governing_body_short)
            else:
                q = q.filter(EventType.governing_body_id.is_(None))

            row = q.first()
            if row:
                return row[0]

            gov_id = None
            if governing_body_short:
                gov = sess.query(GoverningBody).filter_by(short_name=governing_body_short).first()
                gov_id = gov.id if gov else None
            et = EventType(category=category, scoring_system=scoring_system,
                           governing_body_id=gov_id)
            sess.add(et)
            sess.commit()
            return et.id

        if session is not None:
            return _run(session)
        else:
            with create_session() as sess:
                return _run(sess)

    _SCORE_MODELS = {
        "6.0": Score6_0,
        "CJS": ScoreCJS,
        "IJS_component": ScoreIJSComponent,
        "IJS_element": ScoreIJSElement,
    }

    def add_event_with_entries(event_dict, entries_list, scores_by_entry=None,
                               deductions_by_entry=None, costs_list=None,
                               session=None):
        """Create a SkaterEvent with its entries, scores, deductions, and costs.

        Args:
            event_dict: kwargs for SkaterEvent constructor.
            entries_list: list of dicts, each kwargs for EventEntry
                          (event_id is set automatically).
            scores_by_entry: optional dict mapping entry index (int) to a list
                of score dicts.  Each score dict must contain a ``scoring_system``
                key (one of ``"6.0"``, ``"CJS"``, ``"IJS_component"``,
                ``"IJS_element"``) plus the column kwargs for that model.
                ``entry_id`` and ``uSkaterUUID`` are set automatically.
            deductions_by_entry: optional dict mapping entry index (int) to a
                list of deduction dicts with ``deduction_type`` (str) and
                ``value`` (float).  ``entry_id`` and ``uSkaterUUID`` are set
                automatically.
            costs_list: optional list of dicts with ``category`` (str),
                ``amount`` (float), and optionally ``quantity`` (int, default 1)
                and ``note`` (str).
            session: optional external SQLAlchemy session.
        Returns:
            The created SkaterEvent (with entries, scores, deductions, and costs).
        """
        scores_by_entry = scores_by_entry or {}
        deductions_by_entry = deductions_by_entry or {}
        costs_list = costs_list or []

        def _run(sess):
            event_dict.pop("event_cost", None)
            event = SkaterEvent(**event_dict)
            sess.add(event)
            sess.flush()

            for cost_dict in costs_list:
                sess.add(EventCost(
                    event_id=event.id,
                    category=cost_dict["category"],
                    amount=cost_dict["amount"],
                    quantity=cost_dict.get("quantity", 1),
                    note=cost_dict.get("note"),
                ))

            for idx, entry_dict in enumerate(entries_list):
                entry_dict["event_id"] = event.id
                if "uSkaterUUID" not in entry_dict:
                    entry_dict["uSkaterUUID"] = event.uSkaterUUID
                entry = EventEntry(**entry_dict)
                sess.add(entry)
                sess.flush()

                for score_dict in scores_by_entry.get(idx, []):
                    score_dict = dict(score_dict)
                    system = score_dict.pop("scoring_system")
                    model = Event_Data._SCORE_MODELS.get(system)
                    if model is None:
                        raise ValueError(
                            f"Unknown scoring_system '{system}'. "
                            f"Expected one of: {list(Event_Data._SCORE_MODELS)}"
                        )
                    score_dict["entry_id"] = entry.id
                    if "uSkaterUUID" not in score_dict:
                        score_dict["uSkaterUUID"] = event.uSkaterUUID
                    sess.add(model(**score_dict))

                for ded_dict in deductions_by_entry.get(idx, []):
                    sess.add(EventDeduction(
                        entry_id=entry.id,
                        uSkaterUUID=event.uSkaterUUID,
                        deduction_type=ded_dict["deduction_type"],
                        value=ded_dict["value"],
                        notes=ded_dict.get("notes"),
                    ))

            sess.commit()
            sess.refresh(event)
            return event

        if session is not None:
            return _run(session)
        else:
            with create_session() as sess:
                return _run(sess)


    def add_entry(event_id, entry_dict, scores=None, deductions=None, session=None):
        """Add a single entry (with scores and deductions) to an existing event.

        This is the manual-path counterpart to the URL importer's
        ``import_entry_to_event``.  The API wizard calls this when the
        user fills out Steps 2+3 without a URL.

        Args:
            event_id: UUID of the existing SkaterEvent.
            entry_dict: kwargs for EventEntry.  ``event_id`` is set
                automatically.  Must include ``uSkaterUUID``.
            scores: optional list of score dicts, each with a
                ``scoring_system`` key plus column kwargs.
            deductions: optional list of deduction dicts with
                ``deduction_type`` and ``value``.
            session: optional external SQLAlchemy session.
        Returns:
            The created EventEntry.
        """
        scores = scores or []
        deductions = deductions or []

        def _run(sess):
            event = sess.query(SkaterEvent).filter(SkaterEvent.id == event_id).first()
            if not event:
                raise ValueError(f"Event {event_id} not found")

            entry_dict["event_id"] = event.id
            if "uSkaterUUID" not in entry_dict:
                entry_dict["uSkaterUUID"] = event.uSkaterUUID
            entry = EventEntry(**entry_dict)
            sess.add(entry)
            sess.flush()

            for score_dict in scores:
                score_dict = dict(score_dict)
                system = score_dict.pop("scoring_system")
                model = Event_Data._SCORE_MODELS.get(system)
                if model is None:
                    raise ValueError(
                        f"Unknown scoring_system '{system}'. "
                        f"Expected one of: {list(Event_Data._SCORE_MODELS)}"
                    )
                score_dict["entry_id"] = entry.id
                if "uSkaterUUID" not in score_dict:
                    score_dict["uSkaterUUID"] = event.uSkaterUUID
                sess.add(model(**score_dict))

            for ded_dict in deductions:
                sess.add(EventDeduction(
                    entry_id=entry.id,
                    uSkaterUUID=event.uSkaterUUID,
                    deduction_type=ded_dict["deduction_type"],
                    value=ded_dict["value"],
                    notes=ded_dict.get("notes"),
                ))

            sess.commit()
            sess.refresh(entry)
            return entry

        if session is not None:
            return _run(session)
        else:
            with create_session() as sess:
                return _run(sess)


class Music_Data():

    def add_track(tracks, session=None):
        def _run(sess):
            for track in tracks:
                try:
                    sess.add(MusicTrack(**track))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_playlist(playlists, session=None):
        def _run(sess):
            for pl in playlists:
                try:
                    sess.add(MusicPlaylist(**pl))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_playlist_track(entries, session=None):
        def _run(sess):
            for entry in entries:
                try:
                    sess.add(MusicPlaylistTrack(**entry))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)


### Incoming Changes from Legacy

class AddSession:
    def __init__(self, db_session):
        """Store the SQLAlchemy session."""
        self.db_session = db_session

    def __call__(self, data):
        """
        Insert a new Ice_Time row.

        Args:
            data (dict): Keys must match Ice_Time columns.
        Returns:
            Ice_Time: The newly created row object.
        """
        new_row = Ice_Time(**data)

        self.db_session.add(new_row)
        self.db_session.commit()
        self.db_session.refresh(new_row)

        return new_row
