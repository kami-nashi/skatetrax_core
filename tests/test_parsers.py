"""Unit tests for the three results parsers (6.0, IJS, CJS).

Tests only the pure parsing / extraction functions -- no network calls.
HTML fixtures are minimal strings that mirror the real page structure.
"""
import pytest

from skatetrax.utils.results_parser import (
    ParseError as ParseError_6_0,
    _validate_url,
    _split_name_club,
    _clean_cell,
    _infer_level as infer_level_6_0,
    extract_skater_entry as extract_6_0,
)
from skatetrax.utils.results_parser_ijs import (
    ParseError as ParseError_IJS,
    parse_html as parse_html_ijs,
    extract_skater_entry as extract_ijs,
    _infer_level as infer_level_ijs,
    _safe_float,
    _split_name_club as split_name_club_ijs,
)
from skatetrax.utils.results_parser_cjs import (
    parse_html as parse_html_cjs,
    extract_skater_entry as extract_cjs,
    _infer_level as infer_level_cjs,
)

# run via: PYTHONPATH=. pytest tests/test_parsers.py -v


# ═══════════════════════════════════════════════════════════════════════════
# Shared helpers
# ═══════════════════════════════════════════════════════════════════════════

class TestValidateUrl:

    def test_accepts_ijs_domain(self):
        _validate_url("https://ijs.usfigureskating.org/leaderboard/results/2025/30911/218c1.htm")

    def test_rejects_bad_domain(self):
        with pytest.raises(ValueError, match="not in the allow-list"):
            _validate_url("https://evil.com/scores.htm")

    def test_rejects_ftp_scheme(self):
        with pytest.raises(ValueError, match="http or https"):
            _validate_url("ftp://ijs.usfigureskating.org/scores.htm")


class TestSplitNameClub:

    def test_with_club(self):
        name, club = _split_name_club("Ashley Young, Carolinas FSC")
        assert name == "Ashley Young"
        assert club == "Carolinas FSC"

    def test_without_club(self):
        name, club = _split_name_club("Ashley Young")
        assert name == "Ashley Young"
        assert club is None

    def test_extra_whitespace(self):
        name, club = _split_name_club("  Jane Doe ,  Some Club  ")
        assert name == "Jane Doe"
        assert club == "Some Club"

    def test_multiple_commas_uses_first(self):
        name, club = _split_name_club("Smith, Jr., Club A")
        assert name == "Smith"
        assert club == "Jr., Club A"


class TestSafeFloat:

    def test_parses_valid_float(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<td>3.14</td>", "html.parser")
        assert _safe_float(soup.find("td")) == 3.14

    def test_returns_none_for_empty(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<td></td>", "html.parser")
        assert _safe_float(soup.find("td")) is None

    def test_returns_none_for_nbsp(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<td>\xa0</td>", "html.parser")
        assert _safe_float(soup.find("td")) is None

    def test_returns_none_for_none_input(self):
        assert _safe_float(None) is None


# ═══════════════════════════════════════════════════════════════════════════
# 6.0 parser
# ═══════════════════════════════════════════════════════════════════════════

class TestInferLevel6_0:

    def test_strips_gender_and_discipline(self):
        assert infer_level_6_0("Adult High Beginner Women Free Skate - Group B") == "Adult High Beginner"

    def test_no_gender(self):
        assert infer_level_6_0("Adult Bronze Free Skate") == "Adult Bronze Free Skate"

    def test_mens(self):
        assert infer_level_6_0("Adult Silver Men Free Skate") == "Adult Silver"

    def test_empty_returns_none(self):
        assert infer_level_6_0("") is None


class TestExtract6_0:

    PARSED_6_0 = {
        "competition_name": "Test Championship",
        "segment_name": "Adult Bronze Women Free Skate",
        "judge_count": 3,
        "standings": [
            {
                "place": 1,
                "name": "Jane Doe",
                "club": "Test FSC",
                "ordinals": [1, 1, 2],
                "majority": "3/1",
                "tie_breaker": None,
            },
            {
                "place": 2,
                "name": "Ashley Young",
                "club": "Carolinas FSC",
                "ordinals": [2, 2, 1],
                "majority": "3/2",
                "tie_breaker": None,
            },
        ],
        "source_url": "https://ijs.usfigureskating.org/test.htm",
        "fetched_at": "2026-03-01T00:00:00",
        "raw_html": "<html></html>",
    }

    def test_exact_match(self):
        result = extract_6_0(self.PARSED_6_0, "Ashley Young")
        assert result is not None
        assert result["scoring_system"] == "6.0"
        assert result["entry"]["placement"] == 2
        assert result["entry"]["field_size"] == 2
        assert result["matched_name"] == "Ashley Young"
        assert result["matched_club"] == "Carolinas FSC"

    def test_case_insensitive(self):
        result = extract_6_0(self.PARSED_6_0, "ashley young")
        assert result is not None
        assert result["matched_name"] == "Ashley Young"

    def test_partial_match(self):
        result = extract_6_0(self.PARSED_6_0, "Young")
        assert result is not None
        assert result["matched_name"] == "Ashley Young"

    def test_not_found_returns_none(self):
        result = extract_6_0(self.PARSED_6_0, "Nobody Here")
        assert result is None

    def test_scores_6_0_structure(self):
        result = extract_6_0(self.PARSED_6_0, "Ashley Young")
        scores = result["scores_6_0"]
        assert len(scores) == 3
        assert scores[0]["judge_number"] == 1
        assert scores[0]["ordinal"] == 2.0

    def test_event_level_inferred(self):
        result = extract_6_0(self.PARSED_6_0, "Jane Doe")
        assert result["entry"]["event_level"] == "Adult Bronze"


# ═══════════════════════════════════════════════════════════════════════════
# IJS parser
# ═══════════════════════════════════════════════════════════════════════════

class TestInferLevelIJS:

    def test_strips_gender_and_discipline(self):
        assert infer_level_ijs("Adult Gold Women / Free Skate") == "Adult Gold"

    def test_strips_roman_numeral(self):
        assert infer_level_ijs("Adult Gold Women II / Free Skate") == "Adult Gold"

    def test_championship_prefix(self):
        assert infer_level_ijs("Championship Adult Gold Women / Free Skate") == "Championship Adult Gold"

    def test_empty_returns_none(self):
        assert infer_level_ijs("") is None


IJS_HTML = """<html>
<h2 class="title">Test IJS Championship</h2>
<h2 class="catseg">Adult Silver Men / Free Skate</h2>
<table class="sum"><thead><tr>
<th class="rank">Pl.</th><th class="name">Name</th>
<th class="totSeg">TSS</th><th class="totElm">TES</th>
<th class="totComp">TCS</th><th class="totDed">Ded.</th>
</tr></thead><tbody><tr>
<td class="rank">1</td>
<td class="name">Test Skater, Cool FSC</td>
<td class="totSeg">25.50</td>
<td class="totElm">12.00</td>
<td class="totComp">14.50</td>
<td class="totDed">-1.00</td>
</tr></tbody></table>
<table class="elm"><tbody>
<tr><td class="num">1</td><td class="elem">1A</td>
<td class="bv">1.10</td><td class="goe">0.10</td><td class="psv">1.20</td></tr>
<tr><td class="num">2</td><td class="elem">2S</td>
<td class="bv">1.30</td><td class="goe">-0.20</td><td class="psv">1.10</td></tr>
<tr><td class="cn">Composition</td><td class="panel">4.50</td></tr>
<tr><td class="cn">Presentation</td><td class="panel">5.00</td></tr>
<tr><td class="cn">Skating Skills</td><td class="panel">5.00</td></tr>
<tr><td class="gcfv">1.60</td></tr>
</tbody></table>
<table class="ded"><thead><tr>
<th class="total">-1.00</th>
</tr></thead><tbody><tr>
<td class="name">Falls:</td><td class="value">-1.00</td>
</tr></tbody></table>
</html>"""


class TestParseHtmlIJS:

    def test_parses_competition_name(self):
        result = parse_html_ijs(IJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        assert result["competition_name"] == "Test IJS Championship"

    def test_parses_segment_name(self):
        result = parse_html_ijs(IJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        assert result["segment_name"] == "Adult Silver Men / Free Skate"

    def test_scoring_system_tagged(self):
        result = parse_html_ijs(IJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        assert result["scoring_system"] == "IJS"

    def test_standings_count(self):
        result = parse_html_ijs(IJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        assert len(result["standings"]) == 1

    def test_skater_totals(self):
        result = parse_html_ijs(IJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        skater = result["standings"][0]
        assert skater["name"] == "Test Skater"
        assert skater["club"] == "Cool FSC"
        assert skater["total_segment_score"] == 25.50
        assert skater["total_element_score"] == 12.00

    def test_elements_parsed(self):
        result = parse_html_ijs(IJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        elements = result["standings"][0]["elements"]
        assert len(elements) == 2
        assert elements[0]["element_name"] == "1A"
        assert elements[0]["base_value"] == 1.10
        assert elements[1]["element_name"] == "2S"

    def test_components_parsed(self):
        result = parse_html_ijs(IJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        comps = result["standings"][0]["components"]
        assert comps["composition"] == 4.50
        assert comps["presentation"] == 5.00
        assert comps["skating_skills"] == 5.00

    def test_component_factor(self):
        result = parse_html_ijs(IJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        assert result["standings"][0]["component_factor"] == 1.60

    def test_deductions_parsed(self):
        result = parse_html_ijs(IJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        deds = result["standings"][0]["deductions"]
        assert len(deds) == 1
        assert deds[0]["deduction_type"] == "Falls"
        assert deds[0]["value"] == 1.00


class TestExtractIJS:

    def test_extract_skater(self):
        parsed = parse_html_ijs(IJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        result = extract_ijs(parsed, "Test Skater")
        assert result is not None
        assert result["scoring_system"] == "IJS"
        assert result["entry"]["placement"] == 1
        assert result["entry"]["total_segment_score"] == 25.50
        assert len(result["scores_ijs_elements"]) == 2
        assert len(result["scores_ijs_components"]) == 1
        assert len(result["deductions"]) == 1

    def test_not_found(self):
        parsed = parse_html_ijs(IJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        assert extract_ijs(parsed, "Nobody") is None

    def test_level_inferred(self):
        parsed = parse_html_ijs(IJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        result = extract_ijs(parsed, "Test Skater")
        assert result["entry"]["event_level"] == "Adult Silver"


# ═══════════════════════════════════════════════════════════════════════════
# CJS parser
# ═══════════════════════════════════════════════════════════════════════════

class TestInferLevelCJS:

    def test_strips_showcase_suffix(self):
        assert infer_level_cjs("Adult Pre Bronze Lyric-Character-Comedic I,II,III / Showcase") == "Adult Pre Bronze"

    def test_strips_emotional(self):
        assert infer_level_cjs("Adult Bronze Emotional / Showcase") == "Adult Bronze"

    def test_strips_gender(self):
        assert infer_level_cjs("Adult Silver Women / Showcase") == "Adult Silver"


CJS_HTML = """<html>
<h2 class="title">Test CJS Championship</h2>
<h2 class="catseg">Adult Bronze Emotional Women / Showcase</h2>
<table class="sum"><thead><tr>
<th class="rank">Pl.</th><th class="name">Name</th>
<th class="totSeg">TSS</th><th class="totElm">TES</th>
<th class="totComp">TCS</th><th class="totDed">Ded.</th>
</tr></thead><tbody><tr>
<td class="rank">1</td>
<td class="name">Dan Molino, Some Club</td>
<td class="totSeg">15.75</td>
<td class="totElm">0.00</td>
<td class="totComp">15.75</td>
<td class="totDed">0.00</td>
</tr></tbody></table>
<table class="elm"><tbody>
<tr><td class="cn">Artistic Appeal</td><td class="panel">5.50</td></tr>
<tr><td class="cn">Performance</td><td class="panel">5.25</td></tr>
<tr><td class="cn">Skating Skills</td><td class="panel">5.00</td></tr>
</tbody></table>
<table class="ded"><thead><tr>
<th class="total">0.00</th>
</tr></thead><tbody></tbody></table>
</html>"""


class TestParseHtmlCJS:

    def test_parses_competition_name(self):
        result = parse_html_cjs(CJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        assert result["competition_name"] == "Test CJS Championship"

    def test_scoring_system_tagged(self):
        result = parse_html_cjs(CJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        assert result["scoring_system"] == "CJS"

    def test_components_parsed(self):
        result = parse_html_cjs(CJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        comps = result["standings"][0]["components"]
        assert comps["artistic_appeal"] == 5.50
        assert comps["performance"] == 5.25
        assert comps["skating_skills"] == 5.00

    def test_no_deductions_when_zero(self):
        result = parse_html_cjs(CJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        assert result["standings"][0]["deductions"] == []


class TestExtractCJS:

    def test_extract_skater(self):
        parsed = parse_html_cjs(CJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        result = extract_cjs(parsed, "Dan Molino")
        assert result is not None
        assert result["scoring_system"] == "CJS"
        assert result["entry"]["placement"] == 1
        assert len(result["scores_cjs"]) == 1
        assert result["scores_cjs"][0]["artistic_appeal"] == 5.50
        assert result["scores_cjs"][0]["performance"] == 5.25

    def test_level_inferred(self):
        parsed = parse_html_cjs(CJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        result = extract_cjs(parsed, "Dan Molino")
        assert result["entry"]["event_level"] == "Adult Bronze"

    def test_not_found(self):
        parsed = parse_html_cjs(CJS_HTML, "https://ijs.usfigureskating.org/test.htm")
        assert extract_cjs(parsed, "Nobody") is None


# ═══════════════════════════════════════════════════════════════════════════
# Error handling
# ═══════════════════════════════════════════════════════════════════════════

class TestParseErrors:

    def test_ijs_missing_names_raises(self):
        html = "<html><h2 class='other'>Stuff</h2></html>"
        with pytest.raises(ParseError_IJS, match="Could not extract"):
            parse_html_ijs(html, "https://ijs.usfigureskating.org/test.htm")

    def test_ijs_no_sum_tables_raises(self):
        html = """<html>
        <h2 class="title">Test</h2>
        <h2 class="catseg">Segment</h2>
        </html>"""
        with pytest.raises(ParseError_IJS, match="No summary tables"):
            parse_html_ijs(html, "https://ijs.usfigureskating.org/test.htm")
