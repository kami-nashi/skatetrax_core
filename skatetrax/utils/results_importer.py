"""Orchestrate URL-based results imports: parse, persist, and log.

Ties the pure parser (results_parser) to the database layer
(Event_Data, ImportLog) in a single transaction-safe workflow.
"""
from __future__ import annotations

from datetime import datetime, timezone

import requests

from ..models.cyberconnect2 import create_session
from ..models.t_events import (
    ImportLog, SkaterEvent, EventEntry, EventType, EventDeduction,
    Score6_0, ScoreCJS, ScoreIJSComponent, ScoreIJSElement,
)
from . import results_parser as parser_6_0
from . import results_parser_ijs as parser_ijs
from . import results_parser_cjs as parser_cjs

# FK-target models must be imported so SQLAlchemy metadata can resolve
# the foreign keys on SkaterEvent / EventEntry (coaches, locations, etc.)
import skatetrax.models.t_coaches  # noqa: F401
import skatetrax.models.t_locations  # noqa: F401
import skatetrax.models.t_skaterMeta  # noqa: F401
import skatetrax.models.t_equip  # noqa: F401


def import_from_url(
    url: str,
    skater_name: str,
    uSkaterUUID,
    event_date,
    event_overrides: dict | None = None,
) -> dict:
    """Fetch a USFSA results URL, find the skater, and persist the event.

    Args:
        url: Full URL to a USFSA results page.
        skater_name: Name to search for in the standings (e.g. "Ashley Young").
        uSkaterUUID: UUID of the skater account that owns this result.
        event_date: date or datetime -- required since the page doesn't include it.
        event_overrides: Optional dict of extra fields.  Accepted keys for the
            parent event: event_location, coach_id, hosting_club, event_cost,
            notes, uSkaterConfig.  Accepted keys for the entry: entry_date,
            category (defaults to "Competition").

    Returns:
        {"status": "success", "event_id": str, "entry_id": str, "preview": dict}
        {"status": "already_imported", "message": str}
        {"status": "skater_not_found", "message": str, "standings": list}
        {"status": "fetch_error", "message": str}
        {"status": "parse_error", "message": str}
    """
    event_overrides = event_overrides or {}
    raw_html = None

    with create_session() as sess:
        # ── Duplicate check ─────────────────────────────────────────
        existing = (
            sess.query(ImportLog)
            .filter(
                ImportLog.source_url == url,
                ImportLog.uSkaterUUID == uSkaterUUID,
                ImportLog.status == "success",
            )
            .first()
        )
        if existing:
            return {
                "status": "already_imported",
                "message": f"This URL was already imported on {existing.created_at.isoformat()}",
            }

        # ── Fetch + parse (auto-detect scoring system) ────────────
        try:
            raw_html = _prefetch(url)
            parser = _select_parser(url, raw_html)
            if hasattr(parser, "parse_html"):
                parsed = parser.parse_html(raw_html, url)
            else:
                parsed = parser.fetch_and_parse(url)
            raw_html = parsed.get("raw_html", raw_html)
        except (requests.RequestException, ValueError) as exc:
            _write_log(sess, url, "fetch_error", skater_name, uSkaterUUID,
                       error_message=str(exc))
            return {"status": "fetch_error", "message": str(exc)}
        except (parser_6_0.ParseError, parser_ijs.ParseError, parser_cjs.ParseError) as exc:
            _write_log(sess, url, "parse_error", skater_name, uSkaterUUID,
                       raw_html=raw_html, error_message=str(exc))
            return {"status": "parse_error", "message": str(exc)}

        # ── Find skater ─────────────────────────────────────────────
        result = parser.extract_skater_entry(parsed, skater_name)
        if result is None:
            names_on_page = [r["name"] for r in parsed["standings"]]
            _write_log(sess, url, "skater_not_found", skater_name, uSkaterUUID,
                       raw_html=raw_html,
                       error_message=f"Searched for '{skater_name}', found: {names_on_page}")
            return {
                "status": "skater_not_found",
                "message": f"'{skater_name}' not found in results",
                "standings": names_on_page,
            }

        # ── Build and persist ───────────────────────────────────────
        scoring_system = result.get("scoring_system", "6.0")
        category = event_overrides.get("category", "Competition")

        event_dict = {
            "event_label": result["event"]["event_label"],
            "event_date": event_date,
            "uSkaterUUID": uSkaterUUID,
            **{k: v for k, v in event_overrides.items()
               if k in ("event_location", "coach_id", "hosting_club",
                         "notes", "uSkaterConfig")},
        }

        event = SkaterEvent(**event_dict)
        sess.add(event)
        sess.flush()

        entry, entry_meta = _build_entry(
            sess, event.id, uSkaterUUID, event_date, result,
            scoring_system, category, event_overrides,
        )

        _write_log(
            sess, url, "success", skater_name, uSkaterUUID,
            skater_name_matched=result.get("matched_name"),
            event_id=event.id,
            entry_id=entry.id,
        )

        sess.commit()

        return {
            "status": "success",
            "event_id": str(event.id),
            "entry_id": str(entry.id),
            "preview": {
                "event_label": event.event_label,
                "event_date": str(event.event_date),
                **entry_meta,
            },
        }


def import_entry_to_event(
    url: str,
    skater_name: str,
    uSkaterUUID,
    event_id,
    entry_date=None,
    event_overrides: dict | None = None,
) -> dict:
    """Parse a URL and attach the resulting entry to an existing SkaterEvent.

    Use this for the wizard loop -- the parent event already exists from
    Step 1, and the user is adding another entry via URL in Step 2.

    Args:
        url: Full URL to a USFSA results page.
        skater_name: Name to search for in the standings.
        uSkaterUUID: UUID of the skater account.
        event_id: UUID of the existing SkaterEvent to attach to.
        entry_date: date for this specific entry (defaults to parent event_date).
        event_overrides: Optional dict; accepted keys: entry_date, category.

    Returns:
        Same shape as import_from_url.
    """
    event_overrides = event_overrides or {}
    if entry_date:
        event_overrides.setdefault("entry_date", entry_date)
    raw_html = None

    with create_session() as sess:
        event = sess.query(SkaterEvent).filter(SkaterEvent.id == event_id).first()
        if not event:
            return {"status": "error", "message": f"Event {event_id} not found"}

        # ── Duplicate check ─────────────────────────────────────────
        existing = (
            sess.query(ImportLog)
            .filter(
                ImportLog.source_url == url,
                ImportLog.uSkaterUUID == uSkaterUUID,
                ImportLog.status == "success",
            )
            .first()
        )
        if existing:
            return {
                "status": "already_imported",
                "message": f"This URL was already imported on {existing.created_at.isoformat()}",
            }

        # ── Fetch + parse ───────────────────────────────────────────
        try:
            raw_html = _prefetch(url)
            parser = _select_parser(url, raw_html)
            if hasattr(parser, "parse_html"):
                parsed = parser.parse_html(raw_html, url)
            else:
                parsed = parser.fetch_and_parse(url)
            raw_html = parsed.get("raw_html", raw_html)
        except (requests.RequestException, ValueError) as exc:
            _write_log(sess, url, "fetch_error", skater_name, uSkaterUUID,
                       error_message=str(exc))
            return {"status": "fetch_error", "message": str(exc)}
        except (parser_6_0.ParseError, parser_ijs.ParseError, parser_cjs.ParseError) as exc:
            _write_log(sess, url, "parse_error", skater_name, uSkaterUUID,
                       raw_html=raw_html, error_message=str(exc))
            return {"status": "parse_error", "message": str(exc)}

        # ── Find skater ─────────────────────────────────────────────
        result = parser.extract_skater_entry(parsed, skater_name)
        if result is None:
            names_on_page = [r["name"] for r in parsed["standings"]]
            _write_log(sess, url, "skater_not_found", skater_name, uSkaterUUID,
                       raw_html=raw_html,
                       error_message=f"Searched for '{skater_name}', found: {names_on_page}")
            return {
                "status": "skater_not_found",
                "message": f"'{skater_name}' not found in results",
                "standings": names_on_page,
            }

        # ── Build entry on existing event ─────────────────────────
        scoring_system = result.get("scoring_system", "6.0")
        category = event_overrides.get("category", "Competition")

        entry, entry_meta = _build_entry(
            sess, event.id, uSkaterUUID, event.event_date, result,
            scoring_system, category, event_overrides,
        )

        _write_log(
            sess, url, "success", skater_name, uSkaterUUID,
            skater_name_matched=result.get("matched_name"),
            event_id=event.id,
            entry_id=entry.id,
        )

        sess.commit()

        return {
            "status": "success",
            "event_id": str(event.id),
            "entry_id": str(entry.id),
            "preview": {
                "event_label": event.event_label,
                "event_date": str(event.event_date),
                **entry_meta,
            },
        }


def _build_entry(sess, event_id, uSkaterUUID, event_date, result,
                 scoring_system, category, event_overrides):
    """Create an EventEntry with scores and deductions. Returns (entry, preview_meta)."""
    event_type_id = _resolve_event_type(sess, category, scoring_system, "USFSA")

    entry_dict = {
        "event_id": event_id,
        "uSkaterUUID": uSkaterUUID,
        "entry_date": event_overrides.get("entry_date", event_date),
        "event_segment": result["entry"]["event_segment"],
        "event_level": result["entry"]["event_level"],
        "event_type": event_type_id,
        "placement": result["entry"]["placement"],
        "field_size": result["entry"]["field_size"],
        "majority": result["entry"].get("majority"),
        "total_segment_score": result["entry"].get("total_segment_score"),
        "source_url": result["entry"]["source_url"],
    }
    entry = EventEntry(**entry_dict)
    sess.add(entry)
    sess.flush()

    _persist_scores(sess, entry.id, uSkaterUUID, scoring_system, result)
    _persist_deductions(sess, entry.id, uSkaterUUID, result)

    preview_meta = {
        "scoring_system": scoring_system,
        "category": category,
        "segment": entry.event_segment,
        "level": entry.event_level,
        "placement": entry.placement,
        "field_size": entry.field_size,
        "majority": entry.majority,
        "total_segment_score": entry.total_segment_score,
        "matched_name": result.get("matched_name"),
        "matched_club": result.get("matched_club"),
    }
    return entry, preview_meta


def _write_log(sess, url, status, skater_name, uSkaterUUID, *,
               skater_name_matched=None, event_id=None, entry_id=None,
               raw_html=None, error_message=None):
    """Write an ImportLog row within the caller's session."""
    log = ImportLog(
        source_url=url,
        status=status,
        skater_name_searched=skater_name,
        uSkaterUUID=uSkaterUUID,
        skater_name_matched=skater_name_matched,
        event_id=event_id,
        entry_id=entry_id,
        raw_html=raw_html,
        error_message=error_message,
        created_at=datetime.now(timezone.utc),
    )
    sess.add(log)
    if status != "success":
        sess.commit()


def _prefetch(url: str) -> str:
    """Fetch page HTML once so we can inspect it before choosing a parser."""
    resp = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "Skatetrax/1.0 (results importer)"},
    )
    resp.raise_for_status()
    return resp.text


def _select_parser(url: str, raw_html: str | None = None):
    """Pick the correct parser module based on URL pattern and page content.

    - Non-SEGM pages (e.g. ordinal .htm pages) -> 6.0
    - SEGM pages with "Artistic Appeal" in components -> CJS
    - SEGM pages otherwise -> IJS
    """
    from urllib.parse import urlparse
    import os

    path = urlparse(url).path
    basename = os.path.basename(path).upper()

    if not (basename.startswith("SEGM") and basename.endswith(".HTML")):
        return parser_6_0

    if raw_html and "artistic appeal" in raw_html.lower():
        return parser_cjs

    return parser_ijs


def _persist_deductions(sess, entry_id, uSkaterUUID, result):
    """Write EventDeduction rows from the parser result."""
    for ded in result.get("deductions", []):
        sess.add(EventDeduction(
            entry_id=entry_id,
            uSkaterUUID=uSkaterUUID,
            deduction_type=ded["deduction_type"],
            value=ded["value"],
        ))


def _persist_scores(sess, entry_id, uSkaterUUID, scoring_system, result):
    """Write score rows to the correct table(s) based on scoring_system."""
    common = {"entry_id": entry_id, "uSkaterUUID": uSkaterUUID}

    if scoring_system == "6.0":
        for sd in result.get("scores_6_0", []):
            sess.add(Score6_0(**common, **sd))

    elif scoring_system == "CJS":
        for sd in result.get("scores_cjs", []):
            sess.add(ScoreCJS(**common, **sd))

    elif scoring_system == "IJS":
        for sd in result.get("scores_ijs_components", []):
            sess.add(ScoreIJSComponent(**common, **sd))
        for sd in result.get("scores_ijs_elements", []):
            sess.add(ScoreIJSElement(**common, **sd))


def _resolve_event_type(sess, category, scoring_system, governing_body_short):
    """Delegate to Event_Data.resolve_event_type using the caller's session."""
    from ..models.ops.pencil import Event_Data
    return Event_Data.resolve_event_type(
        category, scoring_system, governing_body_short, session=sess,
    )
