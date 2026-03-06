"""Parse USFSA IJS results pages from ijs.usfigureskating.org.

Pure utility -- no Flask dependency, no database writes.  Returns
structured dicts suitable for the results importer.

IJS pages have a repeating per-skater structure:
  1. table.sum  -- summary (place, name, totals)
  2. table.elm  -- executed elements + program components
  3. table.ded  -- deductions
  4. table.maj  -- majority deductions (usually empty)
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
    """Raised when HTML structure doesn't match the expected IJS format."""


def fetch_and_parse(url: str) -> dict:
    """Fetch a USFSA IJS results page and return structured data for all skaters.

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
                    "elements": [
                        {
                            "element_number": int,
                            "element_name": str,
                            "base_value": float,
                            "goe": float,
                            "final_score": float,
                        }, ...
                    ],
                    "components": {
                        "composition": float | None,
                        "presentation": float | None,
                        "skating_skills": float | None,
                    },
                    "component_factor": float,
                    "deductions": [
                        {"deduction_type": str, "value": float}, ...
                    ],
                }, ...
            ],
            "scoring_system": "IJS",
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

    return parse_html(resp.text, url)


def parse_html(raw_html: str, url: str) -> dict:
    """Parse already-fetched HTML as an IJS results page."""
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
            elements, components, comp_factor = _parse_elements_and_components(elm_tables[idx])
            skater["elements"] = elements
            skater["components"] = components
            skater["component_factor"] = comp_factor
        else:
            skater["elements"] = []
            skater["components"] = {"composition": None, "presentation": None, "skating_skills": None}
            skater["component_factor"] = 1.0

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
        "scoring_system": "IJS",
        "source_url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "raw_html": raw_html,
    }


def extract_skater_entry(parsed: dict, skater_name: str) -> dict | None:
    """Find a skater in parsed IJS standings and return a dict ready for persistence.

    Name matching is case-insensitive.  Returns None if not found.
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

    ijs_elements = [
        {
            "element_number": el["element_number"],
            "element_name": el["element_name"],
            "base_value": el["base_value"],
            "goe": el["goe"],
            "final_score": el["final_score"],
        }
        for el in matched_row["elements"]
    ]

    comp = matched_row["components"]
    ijs_components = [
        {
            "judge_number": 0,
            "composition": comp.get("composition"),
            "presentation": comp.get("presentation"),
            "skating_skills": comp.get("skating_skills"),
        }
    ]

    deductions = [
        {"deduction_type": d["deduction_type"], "value": d["value"]}
        for d in matched_row.get("deductions", [])
    ]

    return {
        "scoring_system": "IJS",
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
        "scores_ijs_components": ijs_components,
        "scores_ijs_elements": ijs_elements,
        "deductions": deductions,
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


def _extract_direct_text(soup, tag, css_class):
    """Extract only the direct text node from the first matching tag.

    The USFSA HTML has a mismatched </H1> close tag on the title <H2>,
    which causes html.parser to nest subsequent siblings inside it.
    Using .contents[0] grabs only the first text node.
    """
    el = soup.find(tag, class_=css_class)
    if el is None:
        return None
    for child in el.children:
        if isinstance(child, str):
            txt = child.strip()
            if txt:
                return txt
    return el.get_text(strip=True)


def _parse_summary(sum_table) -> dict | None:
    """Extract place, name, club, and score totals from a table.sum."""
    tbody = sum_table.find("tbody")
    if not tbody:
        return None
    row = tbody.find("tr")
    if not row:
        return None

    rank_td = row.find("td", class_="rank")
    name_td = row.find("td", class_="name")
    seg_td = row.find("td", class_="totSeg")
    elm_td = row.find("td", class_="totElm")
    comp_td = row.find("td", class_="totComp")
    ded_td = row.find("td", class_="totDed")

    if not rank_td or not name_td:
        return None

    try:
        place = int(rank_td.get_text(strip=True))
    except (ValueError, TypeError):
        return None

    name, club = _split_name_club(name_td.get_text(strip=True))

    return {
        "place": place,
        "name": name,
        "club": club,
        "total_segment_score": _safe_float(seg_td),
        "total_element_score": _safe_float(elm_td),
        "total_component_score": _safe_float(comp_td),
        "total_deductions": _safe_float(ded_td),
    }


def _parse_elements_and_components(elm_table) -> tuple[list, dict, float]:
    """Extract elements and program components from a table.elm.

    Returns (elements_list, components_dict, component_factor).
    """
    elements = []
    components = {"composition": None, "presentation": None, "skating_skills": None}
    component_factor = 1.0

    tbody = elm_table.find("tbody")
    if not tbody:
        return elements, components, component_factor

    for row in tbody.find_all("tr"):
        num_td = row.find("td", class_="num")
        if num_td:
            el = _parse_element_row(row)
            if el:
                elements.append(el)
            continue

        cn_td = row.find("td", class_="cn")
        if cn_td:
            comp_name = cn_td.get_text(strip=True).lower()
            panel_td = row.find("td", class_="panel")
            panel_val = _safe_float(panel_td)

            if "composition" in comp_name:
                components["composition"] = panel_val
            elif "presentation" in comp_name:
                components["presentation"] = panel_val
            elif "skating skill" in comp_name:
                components["skating_skills"] = panel_val
            continue

        gcf_td = row.find("td", class_="gcfv")
        if gcf_td:
            try:
                component_factor = float(gcf_td.get_text(strip=True))
            except (ValueError, TypeError):
                pass

    return elements, components, component_factor


def _parse_element_row(row) -> dict | None:
    """Extract a single element from an elements table row."""
    num_td = row.find("td", class_="num")
    elem_td = row.find("td", class_="elem")
    bv_td = row.find("td", class_="bv")
    goe_td = row.find("td", class_="goe")
    psv_td = row.find("td", class_="psv")

    if not num_td or not elem_td:
        return None

    try:
        element_number = int(num_td.get_text(strip=True))
    except (ValueError, TypeError):
        return None

    element_name = elem_td.get_text(strip=True)

    base_value = _safe_float(bv_td)
    goe = _safe_float(goe_td)
    final_score = _safe_float(psv_td)

    if element_name and (base_value is not None or final_score is not None):
        return {
            "element_number": element_number,
            "element_name": element_name,
            "base_value": base_value or 0.0,
            "goe": goe or 0.0,
            "final_score": final_score or 0.0,
        }
    return None


def _parse_deductions(ded_table) -> list[dict]:
    """Extract deductions from a table.ded.

    The header contains the total deduction in th.total (e.g. "-1.00").
    The tbody has name/value pairs as adjacent td.name + td.value cells:
      ['', 'Time violation:', '-0.50', 'Falls:', '-0.50']
    """
    deductions = []

    header = ded_table.find("thead")
    if header:
        total_th = header.find("th", class_="total")
        if total_th:
            total_text = total_th.get_text(strip=True).lstrip("-")
            try:
                if float(total_text) == 0.0:
                    return deductions
            except (ValueError, TypeError):
                pass

    tbody = ded_table.find("tbody")
    if not tbody:
        return deductions

    for row in tbody.find_all("tr"):
        name_cells = row.find_all("td", class_="name")
        value_cells = row.find_all("td", class_="value")

        for name_td, val_td in zip(name_cells, value_cells):
            name_text = name_td.get_text(strip=True).rstrip(":")
            val_text = val_td.get_text(strip=True).lstrip("-")
            if not name_text or not val_text:
                continue
            try:
                val = float(val_text)
                if val > 0:
                    deductions.append({
                        "deduction_type": name_text,
                        "value": val,
                    })
            except (ValueError, TypeError):
                pass

    return deductions


def _split_name_club(text: str) -> tuple[str, str | None]:
    """Split 'Alyson Hansen, Carolinas FSC' into ('Alyson Hansen', 'Carolinas FSC')."""
    if "," in text:
        parts = text.split(",", 1)
        return parts[0].strip(), parts[1].strip()
    return text.strip(), None


def _safe_float(td) -> float | None:
    """Extract a float from a td element, returning None on failure."""
    if td is None:
        return None
    text = td.get_text(strip=True)
    if not text or text == "\xa0":
        return None
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def _infer_level(segment_name: str) -> str | None:
    """Best-effort extraction of the skating level from the segment name.

    'Championship Adult Gold Women / Free Skate'  -> 'Championship Adult Gold'
    'Adult Gold Women II / Free Skate'             -> 'Adult Gold'
    """
    cleaned = re.sub(
        r"\s*/\s*(Free Skate|Short Program|Original Dance|Free Dance|Compulsory|Pattern Dance).*$",
        "",
        segment_name,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\s+(Men|Women|Ladies|Men's|Women's)(\s+(I{1,3}|IV|V))?\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip() or None
