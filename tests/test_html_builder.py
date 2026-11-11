"""HTML builder assertions."""

from datetime import datetime, timedelta, timezone

from pharma_report.feeds import JOURNALS
from pharma_report.html_builder import _split_list, build_page


def _make_entry(title: str, source: str = "FDA", topics: list[str] | None = None) -> dict:
    return {
        "title": title,
        "link": "https://example.com/a",
        "source": source,
        "published": datetime.now(timezone.utc) - timedelta(hours=2),
        "summary": "",
        "topics": topics or [],
    }


def _regulatory(items: list[dict] | None = None) -> dict[str, list[dict]]:
    """Default: one item per agency, FDA-first ordering."""
    if items is None:
        return {
            "FDA":          [_make_entry("FDA approval headline", source="FDA")],
            "EMA":          [_make_entry("EMA opinion", source="EMA")],
            "Health Canada": [_make_entry("Health Canada notice", source="Health Canada")],
            "PMDA":         [_make_entry("PMDA guidance", source="PMDA")],
        }
    return {"FDA": items, "EMA": [], "Health Canada": [], "PMDA": []}


def _industry() -> list[dict]:
    return [_make_entry("Fierce Pharma test headline", source="Fierce Pharma")]


def _seeded_journals() -> list[dict]:
    js = []
    for j in JOURNALS:
        copy = dict(j)
        copy["entries"] = [_make_entry(f"{j['name']} title 1")]
        js.append(copy)
    return js


def test_page_has_brand_and_legend():
    html = build_page(_regulatory(), _industry(), _seeded_journals())
    assert "ClinTrialist Report" in html
    assert "TOPIC COLORS" in html
    assert "AI/ML" in html and "Adaptive" in html and "Causal" in html


def test_titles_render_verbatim():
    reg = _regulatory([_make_entry("Lower-case Title With Numbers 123")])
    html = build_page(reg, _industry(), _seeded_journals())
    assert "Lower-case Title With Numbers 123" in html


def test_details_panels_present():
    html = build_page(_regulatory(), _industry(), _seeded_journals())
    # 6 collapsible panels: Regulatory Watch + General Medical + gi + immuno + onc + neuro
    assert html.count("<details") == 6


def test_industry_headline_rendered():
    html = build_page(_regulatory(), _industry(), _seeded_journals())
    assert "Fierce Pharma test headline" in html


def test_general_medical_panel_present():
    html = build_page(_regulatory(), _industry(), _seeded_journals())
    assert "GENERAL MEDICAL" in html
    assert "NEJM" in html


def test_regulatory_watch_panel_present():
    html = build_page(_regulatory(), _industry(), _seeded_journals())
    assert "REGULATORY WATCH" in html
    for agency in ("FDA", "EMA", "Health Canada", "PMDA"):
        assert agency in html


def test_topic_color_applied_to_link():
    reg = _regulatory([_make_entry("Title", topics=["ai_ml"])])
    html = build_page(reg, _industry(), _seeded_journals())
    assert "#6a1b9a" in html  # AI/ML purple


def test_secondary_tag_badge_shown():
    reg = _regulatory([_make_entry("Title", topics=["ai_ml", "causal"])])
    html = build_page(reg, _industry(), _seeded_journals())
    assert "[Causal]" in html


def test_split_list_even():
    assert _split_list([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_split_list_uneven():
    assert _split_list([1, 2, 3, 4, 5], 2) == [[1, 2, 3], [4, 5]]


def test_empty_journal_renders_placeholder():
    js = [dict(j, entries=[]) for j in JOURNALS]
    html = build_page({"FDA": [], "EMA": [], "Health Canada": [], "PMDA": []}, [], js)
    assert "No recent articles" in html


def _aged(title: str, hours: float, source: str = "FDA") -> dict:
    e = _make_entry(title, source=source)
    e["published"] = datetime.now(timezone.utc) - timedelta(hours=hours)
    return e


def test_lead_prefers_fresh_fda_within_72h():
    from pharma_report.html_builder import _pick_lead

    reg = {"FDA": [_aged("old fda", 24 * 37), _aged("fresh fda", 10)], "EMA": [_aged("ema", 1, "EMA")]}
    assert _pick_lead(reg)["title"] == "fresh fda"


def test_lead_skips_stale_fda_for_fresh_other_agency():
    from pharma_report.html_builder import _pick_lead

    reg = {"FDA": [_aged("old fda", 24 * 37)], "EMA": [_aged("fresh ema", 5, "EMA")]}
    assert _pick_lead(reg)["title"] == "fresh ema"


def test_lead_falls_back_to_freshest_when_all_stale():
    from pharma_report.html_builder import _pick_lead

    reg = {"FDA": [_aged("a", 24 * 37)], "EMA": [_aged("b", 24 * 10, "EMA")]}
    assert _pick_lead(reg)["title"] == "b"
    assert _pick_lead({"FDA": []}) is None


def test_network_chrome_phone_css_counts_and_no_shadow():
    html = build_page(_regulatory(), _industry(), _seeded_journals())
    assert 'data-section="clintrialist"' in html
    assert "https://gcicc.github.io/suite/network.js" in html
    assert "@media (max-width: 640px)" in html and "column-count: 1" in html
    assert "text-shadow: 3px" not in html
    assert "REGULATORY WATCH</b> <font" in html
