"""Parse USFSA CJS (showcase) results pages from ijs.usfigureskating.org.

CJS pages share the same HTML template as IJS (table.sum / table.elm /
table.ded / table.maj), but the program components are different:
  - Artistic Appeal  (not Composition)
  - Performance      (not Presentation)
  - Skating Skills
and there are no executed elements (element score is always 0.00).
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from .results_parser_ijs import (
    ALLOWED_DOMAINS, REQUEST_TIMEOUT, USER_AGENT,
    ParseError,
    _validate_url, _extract_direct_text, _split_name_club,
    _safe_float, _parse_summary, _parse_deductions,
)

_CJS_COMPONENT_MAP = {
    "artistic appeal": "artistic_appeal",
    "performance": "performance",
    "skating skill": "skating_skills",
}


def fetch_and_parse(url: str) -> dict:
    """Fetch a USFSA CJS results page and return structured data for all skaters.

    Returns:
        {
            "competition_name": str,
            "segment_name": str,
            "standings": [
                {
                    "place": int,
                    "name": str,
                    "club": str | None,
                    "total_segment_score": float,
                    "total_element_score": float,
                    "total_component_score": float,
                    "total_deductions": float,
                    "components": {
                        "artistic_appeal": float | None,
                        "performance": float | None,
                        "skating_skills": float | None,
                    },
                    "deductions": [...],
                }, ...
            ],
            "scoring_system": "CJS",
            "source_url": str,
            "fetched_at": str,
            "raw_html": str,
        }
    """
    _validate_url(url)

    resp = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
    )
    resp.raise_for_status()
    raw_html = resp.text

    return parse_html(raw_html, url)


def parse_html(raw_html: str, url: str) -> dict:
    """Parse already-fetched HTML as a CJS results page."""
    soup = BeautifulSoup(raw_html, "html.parser")

    competition_name = _extract_direct_text(soup, "h2", "title")
    segment_name = _extract_direct_text(soup, "h2", "catseg")

    if not competition_name or not segment_name:
        raise ParseError("Could not extract competition or segment name from page")

    sum_tables = soup.find_all("table", class_="sum")
    elm_tables = soup.find_all("table", class_="elm")
    ded_tables = soup.find_all("table", class_="ded")

    if not sum_tables:
        raise ParseError("No summary tables (table.sum) found on page")

    standings = []
    for idx, sum_tbl in enumerate(sum_tables):
        skater = _parse_summary(sum_tbl)
        if skater is None:
            continue

        if idx < len(elm_tables):
            skater["components"] = _parse_cjs_components(elm_tables[idx])
        else:
            skater["components"] = {
                "artistic_appeal": None, "performance": None, "skating_skills": None,
            }

        if idx < len(ded_tables):
            skater["deductions"] = _parse_deductions(ded_tables[idx])
        else:
            skater["deductions"] = []

        standings.append(skater)

    if not standings:
        raise ParseError("No skater data found on page")

    return {
        "competition_name": competition_name,
        "segment_name": segment_name,
        "standings": standings,
        "scoring_system": "CJS",
        "source_url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "raw_html": raw_html,
    }


def extract_skater_entry(parsed: dict, skater_name: str) -> dict | None:
    """Find a skater in parsed CJS standings and return a dict ready for persistence."""
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

    comp = matched_row["components"]
    scores_cjs = [
        {
            "judge_number": 0,
            "artistic_appeal": comp.get("artistic_appeal"),
            "performance": comp.get("performance"),
            "skating_skills": comp.get("skating_skills"),
        }
    ]

    deductions = [
        {"deduction_type": d["deduction_type"], "value": d["value"]}
        for d in matched_row.get("deductions", [])
    ]

    return {
        "scoring_system": "CJS",
        "event": {
            "event_label": parsed["competition_name"],
            "event_date": None,
        },
        "entry": {
            "event_segment": parsed["segment_name"],
            "event_level": event_level,
            "placement": matched_row["place"],
            "field_size": len(parsed["standings"]),
            "majority": None,
            "total_segment_score": matched_row["total_segment_score"],
            "source_url": parsed["source_url"],
        },
        "scores_cjs": scores_cjs,
        "deductions": deductions,
        "matched_name": matched_row["name"],
        "matched_club": matched_row["club"],
    }


# ── Private helpers ─────────────────────────────────────────────────────

def _parse_cjs_components(elm_table) -> dict:
    """Extract CJS program components (no elements) from a table.elm."""
    components = {"artistic_appeal": None, "performance": None, "skating_skills": None}

    tbody = elm_table.find("tbody")
    if not tbody:
        return components

    for row in tbody.find_all("tr"):
        cn_td = row.find("td", class_="cn")
        if not cn_td:
            continue

        comp_text = cn_td.get_text(strip=True).lower()
        panel_td = row.find("td", class_="panel")
        panel_val = _safe_float(panel_td)

        for keyword, field in _CJS_COMPONENT_MAP.items():
            if keyword in comp_text:
                components[field] = panel_val
                break

    return components


def _infer_level(segment_name: str) -> str | None:
    """Best-effort extraction of the skating level from a CJS segment name.

    'Adult Pre Bronze Lyric-Character-Comedic I,II,III / Showcase'
    -> 'Adult Pre Bronze'
    """
    cleaned = re.sub(
        r"\s*/\s*(Showcase|Free Skate|Short Program).*$",
        "",
        segment_name,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\s+(Lyric|Character|Comedic|Dramatic|Emotional|Interpretive).*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\s+(Men|Women|Ladies|Men's|Women's)(\s+(I{1,3}|IV|V))?\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip() or None
