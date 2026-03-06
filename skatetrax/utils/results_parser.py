"""Parse USFSA 6.0 results pages from ijs.usfigureskating.org.

Pure utility -- no Flask dependency, no database writes.  Returns
structured dicts suitable for Event_Data.add_event_with_entries().
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

ALLOWED_DOMAINS = {"ijs.usfigureskating.org"}
REQUEST_TIMEOUT = 15
USER_AGENT = "Skatetrax/1.0 (results importer)"


class ParseError(Exception):
    """Raised when HTML structure doesn't match the expected format."""


def fetch_and_parse(url: str) -> dict:
    """Fetch a USFSA 6.0 results page and return structured standings data.

    Returns:
        {
            "competition_name": str,
            "segment_name": str,
            "judge_count": int,
            "standings": [
                {
                    "place": int,
                    "name": str,          # first + last only
                    "club": str | None,
                    "ordinals": [int, ...],
                    "majority": str | None,
                    "tie_breaker": str | None,
                },
                ...
            ],
            "source_url": str,
            "fetched_at": str (ISO 8601),
            "raw_html": str,
        }

    Raises:
        ValueError: if URL domain is not in the allow-list.
        requests.RequestException: on network errors.
        ParseError: if the HTML doesn't match the expected structure.
    """
    _validate_url(url)

    resp = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
    )
    resp.raise_for_status()
    raw_html = resp.text

    soup = BeautifulSoup(raw_html, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        raise ParseError("No tables found on page")

    standings_table = tables[0]
    caption = standings_table.find("caption")
    if not caption:
        raise ParseError("Standings table has no caption")

    h2_tags = caption.find_all("h2")
    if len(h2_tags) < 2:
        raise ParseError(f"Expected 2 <h2> tags in caption, found {len(h2_tags)}")

    competition_name = h2_tags[0].get_text(strip=True)
    segment_name = h2_tags[1].get_text(strip=True)

    header_row = standings_table.find("tr")
    if not header_row:
        raise ParseError("No header row in standings table")

    headers = [th.get_text(strip=True) for th in header_row.find_all("th")]
    judge_columns = [h for h in headers if h.isdigit()]
    judge_count = len(judge_columns)
    if judge_count == 0:
        raise ParseError("Could not determine judge count from headers")

    data_rows = standings_table.find_all("tr")[1:]
    standings = []
    for row in data_rows:
        cells = row.find_all("td")
        if len(cells) < 2 + judge_count + 1:
            continue

        place_text = cells[0].get_text(strip=True).rstrip(".")
        try:
            place = int(place_text)
        except ValueError:
            continue

        full_name_text = cells[1].get_text(strip=True)
        name, club = _split_name_club(full_name_text)

        ordinals = []
        for i in range(judge_count):
            cell_text = cells[2 + i].get_text(strip=True)
            try:
                ordinals.append(int(cell_text))
            except ValueError:
                ordinals.append(None)

        maj_idx = 2 + judge_count
        tie_idx = maj_idx + 1

        majority = _clean_cell(cells[maj_idx]) if maj_idx < len(cells) else None
        tie_breaker = _clean_cell(cells[tie_idx]) if tie_idx < len(cells) else None

        standings.append({
            "place": place,
            "name": name,
            "club": club,
            "ordinals": ordinals,
            "majority": majority,
            "tie_breaker": tie_breaker,
        })

    if not standings:
        raise ParseError("No skater rows found in standings table")

    return {
        "competition_name": competition_name,
        "segment_name": segment_name,
        "judge_count": judge_count,
        "standings": standings,
        "source_url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "raw_html": raw_html,
    }


def extract_skater_entry(parsed: dict, skater_name: str) -> dict | None:
    """Find a skater in parsed standings and return a dict ready for persistence.

    Name matching is case-insensitive against the name portion (not the club).
    Returns None if the skater is not found.
    """
    target = skater_name.strip().lower()

    matched_row = None
    for row in parsed["standings"]:
        if row["name"].lower() == target:
            matched_row = row
            break

    if matched_row is None:
        for row in parsed["standings"]:
            if target in row["name"].lower():
                matched_row = row
                break

    if matched_row is None:
        return None

    event_level = _infer_level(parsed["segment_name"])

    scores = [
        {"judge_number": i + 1, "ordinal": float(o) if o is not None else None}
        for i, o in enumerate(matched_row["ordinals"])
    ]

    return {
        "scoring_system": "6.0",
        "event": {
            "event_label": parsed["competition_name"],
            "event_date": None,
        },
        "entry": {
            "event_segment": parsed["segment_name"],
            "event_level": event_level,
            "placement": matched_row["place"],
            "field_size": len(parsed["standings"]),
            "majority": matched_row["majority"],
            "source_url": parsed["source_url"],
        },
        "scores_6_0": scores,
        "matched_name": matched_row["name"],
        "matched_club": matched_row["club"],
    }


# ── Private helpers ─────────────────────────────────────────────────────

def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_DOMAINS:
        raise ValueError(
            f"URL domain '{parsed.hostname}' is not in the allow-list: {ALLOWED_DOMAINS}"
        )
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"URL scheme must be http or https, got '{parsed.scheme}'")


def _split_name_club(text: str) -> tuple[str, str | None]:
    """Split 'Ashley Young, Carolinas FSC' into ('Ashley Young', 'Carolinas FSC')."""
    if "," in text:
        parts = text.split(",", 1)
        return parts[0].strip(), parts[1].strip()
    return text.strip(), None


def _clean_cell(td) -> str | None:
    """Return cell text or None if it's just whitespace / &nbsp;."""
    text = td.get_text(strip=True)
    if not text or text == "\xa0":
        return None
    return text


def _infer_level(segment_name: str) -> str | None:
    """Best-effort extraction of the skating level from the segment name.

    For 'Adult High Beginner Women Free Skate - Group B' returns
    'Adult High Beginner'.  Strips common suffixes like gender, discipline,
    and group designations.
    """
    cleaned = re.sub(
        r"\s*-\s*Group\s+\w+$", "", segment_name, flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"\s+(Men|Women|Ladies|Men's|Women's)\s+(Free Skate|Short Program|Original Dance|Free Dance|Compulsory|Pattern Dance).*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip() or None
