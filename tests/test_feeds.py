"""Sanity tests for the feed registry."""

from pharma_report.feeds import (
    CATEGORIES,
    JOURNALS,
    REGULATORY_AGENCIES,
    REGULATORY_FEEDS,
)


def test_unique_journal_names():
    names = [j["name"] for j in JOURNALS]
    assert len(names) == len(set(names)), "duplicate journal name in JOURNALS"


def test_unique_regulatory_names():
    names = [f["name"] for f in REGULATORY_FEEDS]
    assert len(names) == len(set(names))


def test_journal_categories_valid():
    for j in JOURNALS:
        assert j["category"] in CATEGORIES, f"{j['name']} has invalid category"


def test_journal_fields_present():
    for j in JOURNALS:
        assert j["rss"].startswith(("http://", "https://")), j["name"]
        assert j["home"].startswith(("http://", "https://")), j["name"]


def test_regulatory_fields_present():
    for f in REGULATORY_FEEDS:
        assert f["rss"].startswith(("http://", "https://")), f["name"]
        assert f["agency"] in REGULATORY_AGENCIES, f["name"]


def test_every_category_has_journals():
    for cat in CATEGORIES:
        assert any(j["category"] == cat for j in JOURNALS), f"no journals in {cat}"


def test_every_agency_has_feeds():
    for agency in REGULATORY_AGENCIES:
        assert any(f["agency"] == agency for f in REGULATORY_FEEDS), f"no feeds for {agency}"
